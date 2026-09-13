import os

from common import (
    ROOT_PARTITION,
    ROOT_LABEL,
    UKI_PATH,
    StepError,
    chroot_checked,
    require_success,
    run_command,
)

def _get_root_uuid() -> str:
    """
    Obtém e valida o UUID da partição raiz.
    """
    result = run_command([
        "blkid", "-s", "UUID", "-o", "value",
        ROOT_PARTITION,
    ])
    require_success(
        result,
        f"não foi possível obter o UUID de {ROOT_PARTITION}.",
    )
    uuid = (result.stdout or "").strip()
    if not uuid:
        raise StepError(f"o UUID de {ROOT_PARTITION} não foi retornado pelo blkid.")
    return uuid

def _prepare_uki_directory() -> None:
    """Cria o diretório de destino da UKI definido por UKI_PATH."""
    uki_directory = os.path.dirname(UKI_PATH)
    try:
        os.makedirs(f"/mnt{uki_directory}", exist_ok=True)
    except OSError as error:
        raise StepError(f"não foi possível preparar o diretório da UKI: {error}") from error

def _write_kernel_cmdline() -> None:
    """Escreve a linha de comando do kernel usando o label da raiz."""
    try:
        os.makedirs("/mnt/etc/kernel", exist_ok=True)
        with open("/mnt/etc/kernel/cmdline", "w", encoding="utf-8") as file:
            file.write(f"root=LABEL={ROOT_LABEL} rw\n")
    except OSError as error:
        raise StepError(f"não foi possível configurar /etc/kernel/cmdline: {error}") from error

def _configure_kernel_preset() -> None:
    """
    Escreve o arquivo de preset do mkinitcpio para o linux-zen.
    """
    preset_path = "/mnt/etc/mkinitcpio.d/linux-zen.preset"
    content = (
        "# mkinitcpio preset file for linux-zen\n\n"
        'ALL_config="/etc/mkinitcpio.conf"\n'
        'ALL_kver="/boot/vmlinuz-linux-zen"\n\n'
        "PRESETS=('default')\n\n"
        f'default_uki="{UKI_PATH}"\n'
        'default_options="--cmdline /etc/kernel/cmdline"\n'
    )
    try:
        with open(preset_path, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError as error:
        raise StepError(f"não foi possível configurar o preset do linux-zen: {error}") from error

def _read_mkinitcpio_conf() -> str:
    """
    Lê o conteúdo do arquivo /etc/mkinitcpio.conf.
    """
    config_path = "/mnt/etc/mkinitcpio.conf"
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as error:
        raise StepError(f"não foi possível ler /etc/mkinitcpio.conf: {error}") from error

def _write_mkinitcpio_conf(content: str) -> None:
    """
    Sobrescreve o arquivo /etc/mkinitcpio.conf com o novo conteúdo.
    """
    config_path = "/mnt/etc/mkinitcpio.conf"
    try:
        with open(config_path, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError as error:
        raise StepError(f"não foi possível atualizar /etc/mkinitcpio.conf: {error}") from error

def _has_microcode_in_hooks(content: str) -> bool:
    """
    Verifica se 'microcode' já está presente na linha HOOKS do conteúdo.
    """
    hooks_line = next(
        (line.strip() for line in content.splitlines() if line.strip().startswith("HOOKS=")),
        None,
    )
    if not hooks_line:
        return False
    hooks_value = hooks_line.split("=", 1)[1].strip()
    return hooks_value.startswith("(") and "microcode" in hooks_value[1:-1].split()

def _inject_microcode_into_hooks(content: str) -> str:
    """Insere 'microcode' imediatamente após 'autodetect' na linha HOOKS."""
    lines = content.splitlines(keepends=True)

    for index, line in enumerate(lines):
        stripped = line.lstrip()

        if not stripped.startswith("HOOKS="):
            continue

        prefix = line[:len(line) - len(stripped)]
        newline = "\n" if line.endswith("\n") else ""
        value = stripped.rstrip("\n")

        if not value.startswith("HOOKS=(") or not value.endswith(")"):
            continue

        hooks = value[len("HOOKS=("):-1].strip().split()

        if "autodetect" not in hooks:
            raise StepError("não foi possível localizar 'autodetect' na configuração HOOKS.")

        position = hooks.index("autodetect") + 1
        hooks.insert(position, "microcode")

        lines[index] = f"{prefix}HOOKS=({' '.join(hooks)}){newline}"
        return "".join(lines)

    raise StepError("não foi possível localizar a configuração HOOKS em /etc/mkinitcpio.conf.")

def _ensure_microcode_hook() -> None:
    """
    Garante que o hook 'microcode' esteja configurado no mkinitcpio.conf.
    """
    content = _read_mkinitcpio_conf()
    if _has_microcode_in_hooks(content):
        return
    new_content = _inject_microcode_into_hooks(content)
    _write_mkinitcpio_conf(new_content)

def _install_core_kernel_packages() -> None:
    """
    Instala os pacotes principais do kernel e ferramentas de inicialização.
    """
    chroot_checked(
        [
            "pacman", "-S",
            "--needed", "--noconfirm",
            "mkinitcpio",
            "amd-ucode",
            "linux-zen",
        ],
        "não foi possível instalar mkinitcpio, microcódigo e linux-zen.",
    )

def _install_kernel_dependencies() -> None:
    """
    Instala as dependências do kernel como pacotes secundários.
    """
    chroot_checked(
        [
            "pacman", "-S", "--needed", "--noconfirm", "--asdeps",
            "linux-firmware",
            "linux-zen-headers",
        ],
        "não foi possível instalar as dependencias de kernel linux-firmware e linux-zen-headers.",
    )

def _generate_initramfs() -> None:
    """
    Executa o mkinitcpio para gerar todas as imagens de inicialização configuradas.
    """
    chroot_checked(
        ["mkinitcpio", "-P"],
        "não foi possível gerar a UKI do linux-zen.",
    )

def _cleanup_redundant_boot_files() -> None:
    """
    Remove arquivos de initramfs e microcode redundantes do diretório de boot.
    """
    paths = (
        "/mnt/boot/initramfs-linux-zen.img",
        "/mnt/boot/initramfs-linux-zen-fallback.img",
        "/mnt/boot/amd-ucode.img",
    )
    for path in paths:
        if os.path.exists(path) or os.path.islink(path):
            try:
                os.remove(path)
            except OSError as error:
                raise StepError(f"não foi possível remover {path}: {error}") from error

def _validate_final_installation_state() -> None:
    """
    Verifica se os arquivos essenciais do kernel e da UKI foram gerados corretamente.
    """
    if not os.path.isfile("/mnt/boot/vmlinuz-linux-zen"):
        raise StepError("/boot/vmlinuz-linux-zen não foi encontrado após a instalação do kernel.")
    if not os.path.isfile("/mnt/efi/EFI/Linux/arch-temp-linux-zen.efi"):
        raise StepError("a UKI arch-temp-linux-zen.efi não foi gerada.")

def run() -> None:
    """
    Orquestra a instalação e configuração completa do kernel linux-zen com suporte a UKI.

    O processo é dividido em etapas de responsabilidade única:
    1. Instalação de pacotes principais e dependências.
    2. Preparação do diretório de UKI.
    3. Configuração da linha de comando do kernel (cmdline).
    4. Configuração do preset do mkinitcpio.
    5. Injeção do hook de microcode no mkinitcpio.conf.
    6. Geração do initramfs/UKI.
    7. Limpeza de arquivos de boot redundantes.
    8. Validação final dos arquivos gerados.
    """
    _install_core_kernel_packages()
    _install_kernel_dependencies()
    _prepare_uki_directory()
    
    root_uuid = _get_root_uuid()
    _write_kernel_cmdline(root_uuid)
    
    _configure_kernel_preset()
    _ensure_microcode_hook()
    
    _generate_initramfs()
    _cleanup_redundant_boot_files()
    _validate_final_installation_state()
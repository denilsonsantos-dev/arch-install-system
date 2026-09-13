from common import StepError, chroot_checked

def _uncomment_locale() -> None:
    """
    Descomenta o locale `pt_BR.UTF-8 UTF-8` no arquivo `/etc/locale.gen`
    do sistema instalado usando `sed`.
    """
    chroot_checked(
        [
            "sed", "-i",
            "s/^#pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/",
            "/etc/locale.gen",
        ],
        "não foi possível configurar o locale do sistema instalado.",
    )

def _generate_locales() -> None:
    """
    Executa `locale-gen` no sistema instalado para compilar os locales
    configurados no `/etc/locale.gen`.
    """
    chroot_checked(
        ["locale-gen"],
        "não foi possível gerar o locale do sistema instalado.",
    )

def _write_locale_conf() -> None:
    """
    Cria o arquivo `/mnt/etc/locale.conf` definindo `LANG=pt_BR.UTF-8`
    como locale padrão do sistema.
    """
    try:
        with open("/mnt/etc/locale.conf", "w", encoding="utf-8") as file:
            file.write("LANG=pt_BR.UTF-8\n")
    except OSError as error:
        raise StepError(f"não foi possível gravar o locale.conf: {error}") from error

def _write_vconsole_conf() -> None:
    """
    Cria o arquivo `/mnt/etc/vconsole.conf` definindo `KEYMAP=br-abnt2`
    como layout de teclado para o console virtual.
    """
    try:
        with open("/mnt/etc/vconsole.conf", "w", encoding="utf-8") as file:
            file.write("KEYMAP=br-abnt2\n")
    except OSError as error:
        raise StepError(f"não foi possível gravar o vconsole.conf: {error}") from error

def run() -> None:
    """
    Configura o locale e o layout de teclado do sistema instalado para
    o padrão brasileiro.

    O processo é realizado em quatro etapas independentes:

    1. `_uncomment_locale`: descomenta a linha do locale brasileiro no
       arquivo `/etc/locale.gen` usando `sed` no ambiente chroot.

    2. `_generate_locales`: executa `locale-gen` no ambiente chroot para
       compilar os locales configurados.

    3. `_write_locale_conf`: cria o arquivo `/mnt/etc/locale.conf` no
       sistema hospedeiro definindo `LANG=pt_BR.UTF-8`.

    4. `_write_vconsole_conf`: cria o arquivo `/mnt/etc/vconsole.conf`
       no sistema hospedeiro definindo `KEYMAP=br-abnt2`.

    Caso qualquer etapa falhe, um `StepError` é levantado informando o
    motivo da falha.
    """
    _uncomment_locale()
    _generate_locales()
    _write_locale_conf()
    _write_vconsole_conf()
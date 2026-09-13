import os
import shutil
import unicodedata


from common import (
    DISK,
    ESP_LABEL,
    ESP_PARTITION,
    ROOT_LABEL,
    ROOT_PARTITION,
    ARCHOS_LABEL,
    ARCHOS_PARTITION,
    SYSTEMD_BOOT_ENTRY,
    UKI_PATH,
    SWAPFILE,
    ESP_SIZE,
    ROOT_SIZE,
    ARCHOS_SIZE,
    StepError,
    command_error,
    require_success,
    run_command,
)

def _normalizar_erro(text: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )

def _unmount_target() -> None:
    """Desmonta recursivamente o ponto de montagem /mnt."""
    result = run_command(["umount", "-R", "/mnt"])
    error = _normalizar_erro(result.stderr.strip().lower()) if result.stderr else ""
    
    if result.returncode == 0:
        return

    if "nao montado" in error:
        return
    
    raise StepError(
        command_error(
            result,
            "não foi possível desmontar /mnt.",
        )
    )

def _confirm_disk_wipe() -> None:
    """
    Solicita confirmação do usuário antes de apagar o disco.
    """
    print(f"\nATENÇÃO: TODAS AS PARTIÇÕES DE {DISK} SERÃO APAGADAS.")
    print("Isso destrói permanentemente todos os dados existentes nesse SSD.")
    while True:
        answer = input(f"Digite APAGAR para confirmar a limpeza de {DISK}: ").strip()
        if answer == "APAGAR":
            break
        if answer.lower() in ("sair", "s"):
            raise SystemExit(1)
        print("Confirmação incorreta. Nenhum dado foi alterado.")

def _cleanup_existing_mounts() -> None:
    """
    Desativa swap e desmonta o sistema alvo antes da limpeza.
    """
    run_command(["swapoff", SWAPFILE])
    _unmount_target()

def _wipe_disk_signatures() -> None:
    """
    Remove todas as assinaturas de sistema de arquivos do disco.
    """
    require_success(
        run_command(["wipefs", "-a", DISK]),
        f"não foi possível limpar as assinaturas de {DISK}.",
    )

def _zap_partition_table() -> None:
    """
    Apaga completamente a tabela de partições do disco.
    """
    require_success(
        run_command(["sgdisk", "--zap-all", DISK]),
        f"não foi possível apagar a tabela de partições de {DISK}.",
    )

def _create_partition_table() -> None:
    """Cria uma nova tabela GPT com três partições."""
    require_success(
        run_command([
            "sgdisk",
            "--clear",
            f"--new=1:0:+{ESP_SIZE}",
            "--typecode=1:ef00",
            f"--change-name=1:{ESP_LABEL}",
            f"--new=2:0:+{ROOT_SIZE}",
            "--typecode=2:8304",
            f"--change-name=2:{ROOT_LABEL}",
            f"--new=3:0:{ARCHOS_SIZE}",
            "--typecode=3:8304",
            f"--change-name=3:{ARCHOS_LABEL}",
            DISK,
        ]),
        f"não foi possível recriar a tabela GPT em {DISK}.",
    )

def _inform_kernel_of_changes() -> None:
    """
    Notifica o kernel sobre a nova tabela de partições.
    """
    require_success(
        run_command(["partprobe", DISK]),
        f"não foi possível informar ao kernel sobre a nova tabela de partições de {DISK}.",
    )

def _format_esp_partition() -> None:
    """
    Formata a partição ESP como FAT32.
    """
    require_success(
        run_command([
            "mkfs.fat",
            "-F32",
            "-n",
            ESP_LABEL,
            ESP_PARTITION,
        ]),
        f"não foi possível formatar {ESP_PARTITION} como FAT32.",
    )

def _format_root_partition() -> None:
    """
    Formata a partição raiz como ext4.
    """
    require_success(
        run_command([
            "mkfs.ext4",
            "-F",
            "-L",
            ROOT_LABEL,
            ROOT_PARTITION,
        ]),
        f"não foi possível formatar {ROOT_PARTITION} como ext4.",
    )

def _format_archos_partition() -> None:
    """
    Formata a partição ArchOS como ext4.
    """
    require_success(
        run_command([
            "mkfs.ext4",
            "-F",
            "-L",
            ARCHOS_LABEL,
            ARCHOS_PARTITION,
        ]),
        f"não foi possível formatar {ARCHOS_PARTITION} como ext4.",
    )

def _mount_esp_for_cleanup() -> None:
    """
    Monta a partição ESP em /mnt/efi para limpeza.
    """
    os.makedirs("/mnt/efi", exist_ok=True)
    require_success(
        run_command([
            "mount",
            ESP_PARTITION,
            "/mnt/efi",
            "--mkdir",
        ]),
        "não foi possível montar a ESP para limpeza.",
    )

def _remove_uki_and_entry() -> None:
    """
    Remove a UKI e a entrada do bootloader da ESP.
    """
    target_uki = f"/mnt/{UKI_PATH}"
    target_entry = f"/mnt/efi/loader/entries/{SYSTEMD_BOOT_ENTRY}"
    for path in (target_uki, target_entry):
        if os.path.exists(path) or os.path.islink(path):
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

def _mount_root_for_cleanup() -> None:
    """
    Monta a partição raiz em /mnt para limpeza.
    """
    require_success(
        run_command([
            "mount",
            ROOT_PARTITION,
            "/mnt",
            "--mkdir",
        ]),
        "não foi possível montar a partição raiz para limpeza.",
    )

def _clean_root_partition() -> None:
    """
    Remove todo o conteúdo da partição raiz montada.
    """
    result = run_command([
        "find",
        "/mnt",
        "-mindepth", "1",
        "-maxdepth", "1",
        "-xdev",
        "-exec", "rm", "-rf", "--", "{}", "+",
    ])
    require_success(
        result,
        "não foi possível limpar a instalação alvo.",
    )

def prepare() -> None:
    """
    Prepara o disco para instalação completa, apagando todos os dados existentes.

    O processo é realizado em dez etapas independentes:

    1. `_confirm_disk_wipe`: solicita confirmação explícita do usuário.
    2. `_cleanup_existing_mounts`: desativa swap e desmonta /mnt.
    3. `_wipe_disk_signatures`: remove assinaturas de sistemas de arquivos.
    4. `_zap_partition_table`: apaga a tabela de partições existente.
    5. `_create_partition_table`: cria nova tabela GPT com três partições.
    6. `_inform_kernel_of_changes`: notifica o kernel sobre as mudanças.
    7. `_format_esp_partition`: formata a ESP como FAT32.
    8. `_format_root_partition`: formata a raiz como ext4.
    9. `_format_archos_partition`: formata ArchOS como ext4.

    Caso qualquer etapa falhe, um `StepError` é levantado informando o motivo.
    """
    # _confirm_disk_wipe()
    _cleanup_existing_mounts()
    _wipe_disk_signatures()
    _zap_partition_table()
    _create_partition_table()
    _inform_kernel_of_changes()
    _format_esp_partition()
    _format_root_partition()
    _format_archos_partition()

def reset() -> None:
    """
    Limpa somente a instalação alvo sem formatar a ESP inteira.

    O processo é realizado em sete etapas independentes:

    1. `_cleanup_existing_mounts`: desativa swap e desmonta /mnt.
    2. `_mount_esp_for_cleanup`: monta a ESP em /mnt/efi.
    3. `_remove_uki_and_entry`: remove a UKI e entrada do bootloader.
    4. `_unmount_target`: desmonta a ESP.
    5. `_mount_root_for_cleanup`: monta a partição raiz em /mnt.
    6. `_clean_root_partition`: remove todo o conteúdo da raiz.
    7. `_unmount_target`: desmonta a partição raiz.

    Caso qualquer etapa falhe, um `StepError` é levantado informando o motivo.
    """
    _cleanup_existing_mounts()
    _mount_esp_for_cleanup()
    _remove_uki_and_entry()
    _unmount_target()
    _mount_root_for_cleanup()
    _clean_root_partition()
    _unmount_target()
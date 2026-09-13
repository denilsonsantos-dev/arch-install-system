import os

from common import (
    SYSTEMD_BOOT_ENTRY,
    SYSTEMD_BOOT_TITLE,
    UKI_BASE_PATH,
    StepError,
    require_success,
    run_command,
)

LOADER_DIR = "/mnt/efi/loader"
ENTRIES_DIR = os.path.join(LOADER_DIR, "entries")

def _should_install_bootloader():
    answer = input("Instalar o bootloader? [S/N]: ").strip().lower()
    return answer in ("s", "sim", "y", "yes")

def _install_bootloader():
    result = run_command([
        "bootctl",
        "--esp-path=/mnt/efi",
        "install",
    ])
    require_success(result, "não foi possível instalar o systemd-boot.")

def _create_entries_directory():
    os.makedirs(ENTRIES_DIR, exist_ok=True)

def _create_loader_config():
    loader_conf = os.path.join(LOADER_DIR, "loader.conf")

    if os.path.exists(loader_conf):
        return

    with open(loader_conf, "w", encoding="utf-8") as file:
        file.write("timeout 5\neditor no\n")

def _create_boot_entry():
    entry_path = os.path.join(ENTRIES_DIR, SYSTEMD_BOOT_ENTRY)
    with open(entry_path, "w", encoding="utf-8") as file:
        file.write(
            f"title {SYSTEMD_BOOT_TITLE}\n"
            f"efi {UKI_BASE_PATH}\n"
        )

def _configure_bootloader_files():
    try:
        _create_entries_directory()
        _create_loader_config()
        _create_boot_entry()
    except OSError as error:
        raise StepError(f"não foi possível criar a configuração do systemd-boot: {error}") from error

def run():
    if _should_install_bootloader():
        _install_bootloader()
    _configure_bootloader_files()
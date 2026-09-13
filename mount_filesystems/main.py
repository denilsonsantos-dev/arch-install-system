import os

from common import (
    ESP_PARTITION,
    ROOT_PARTITION,
    StepError,
    command_error,
    require_success,
    run_command,
)


def run():
    if not os.path.exists(ROOT_PARTITION):
        raise StepError(f"partição raiz não encontrada: {ROOT_PARTITION}")

    if not os.path.exists(ESP_PARTITION):
        raise StepError(f"partição EFI não encontrada: {ESP_PARTITION}")

    os.makedirs("/mnt/efi", exist_ok=True)

    result = run_command(["mount", ROOT_PARTITION, "/mnt", "--mkdir"])
    require_success(result, f"não foi possível montar {ROOT_PARTITION} em /mnt.")

    result = run_command(["mount", ESP_PARTITION, "/mnt/efi", "--mkdir"])
    if result.returncode != 0:
        run_command(["umount", "/mnt"])
        raise StepError(
            command_error(result,
                f"não foi possível montar {ESP_PARTITION} em /mnt/efi.",
            )
        )
from common import StepError, require_success, run_command


def run():
    result = run_command(["genfstab", "-L", "/mnt"])
    require_success(result, "não foi possível gerar o fstab.")

    try:
        with open("/mnt/etc/fstab", "w", encoding="utf-8") as fstab:
            fstab.write(result.stdout)
    except OSError as error:
        raise StepError(f"não foi possível gravar o fstab: {error}") from error

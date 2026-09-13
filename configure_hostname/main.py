from common import StepError

def run():
    try:
        with open("/mnt/etc/hostname", "w", encoding="utf-8") as file:
            file.write("ARCH-DESKTOP\n")
    except OSError as error:
        raise StepError(f"não foi possível configurar o hostname: {error}") from error
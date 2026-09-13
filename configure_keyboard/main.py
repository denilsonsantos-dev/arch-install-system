from common import require_success, run_command


def run():
    result = run_command(["loadkeys", "br-abnt2"])
    require_success(result, "não foi possível configurar o teclado.")
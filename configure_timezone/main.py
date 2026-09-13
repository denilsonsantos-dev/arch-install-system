from common import require_success, run_command


def run():
    for command in (
        ["timedatectl", "set-timezone", "America/Bahia"],
        ["timedatectl", "set-ntp", "true"],
    ):
        result = run_command(command)
        require_success(result, f"não foi possível executar {' '.join(command)}.")

from common import require_success, run_command

def run():
    result = run_command(["ping", "-c", "1", "ping.archlinux.org"])
    require_success(result, "não foi possível conectar à internet.")
from common import require_success, run_command


def run():
    result = run_command(["pacstrap", "-K", "/mnt", "base"])
    require_success(result, "não foi possível instalar o sistema base.")
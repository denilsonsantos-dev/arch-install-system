from common import SWAPFILE, require_success, run_command

def run():
    result = run_command(["swapon", SWAPFILE])
    require_success(result, "não foi possível ativar o swapfile.")
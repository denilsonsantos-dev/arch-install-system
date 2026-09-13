from common import SWAPFILE, SWAP_SIZE_MB, require_success, run_command

def _create_swapfile():
    result = run_command([
        "fallocate",
        "-l",
        f"{SWAP_SIZE_MB}M",
        SWAPFILE,
    ])
    require_success(result, "não foi possível criar o swapfile.")

def _set_swapfile_permissions():
    result = run_command(["chmod", "600", SWAPFILE])
    require_success(result, "não foi possível ajustar a permissão do swapfile.")

def _initialize_swapfile():
    result = run_command(["mkswap", SWAPFILE])
    require_success(result, "não foi possível inicializar o swapfile.")

def run():
    _create_swapfile()
    _set_swapfile_permissions()
    _initialize_swapfile()
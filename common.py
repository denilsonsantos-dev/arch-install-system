import subprocess
from _install_system_presets.test import *

class StepError(Exception):
    """Falha recuperável em uma etapa da instalação."""

def command_error(result, fallback):
    stderr = (result.stderr or "").strip()
    return stderr or fallback

def run_command(command, interactive=False):
    if interactive:
        return subprocess.run(command)

    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

def require_success(result, fallback):
    if result.returncode != 0:
        raise StepError(command_error(result, fallback))
    return result

def chroot(command, interactive=False):
    return run_command(
        ["arch-chroot", "/mnt", *command],
        interactive=interactive,
    )

def chroot_checked(command, fallback, interactive=False):
    return require_success(
        chroot(command, interactive=interactive),
        fallback,
    )
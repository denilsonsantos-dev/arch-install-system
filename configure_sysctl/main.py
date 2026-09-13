import os
from typing import Dict, Optional
from common import StepError

DEFAULT_SYSCTL_CONFIGS: Dict[str, str] = {
    "99-swappiness.conf": "vm.swappiness=2\n",
    "boot.conf": "kernel.printk = 3 3 3 3\n",
}

def _apply_sysctl_configs(target_root: str, configs: Dict[str, str]) -> None:
    sysctl_dir = os.path.join(target_root, "etc", "sysctl.d")
    os.makedirs(sysctl_dir, exist_ok=True)
    for filename, content in configs.items():
        filepath = os.path.join(sysctl_dir, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

def run(target_root: str = "/mnt", configs: Optional[Dict[str, str]] = None) -> None:
    configs = configs if configs is not None else DEFAULT_SYSCTL_CONFIGS
    try:
        _apply_sysctl_configs(target_root, configs)
    except OSError as error:
        raise StepError(f"não foi possível configurar o sysctl: {error}") from error
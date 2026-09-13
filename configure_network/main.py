from common import chroot_checked

def _install_networkmanager() -> None:
    """
    Instala o pacote `networkmanager` no sistema instalado usando `pacman`.

    :raises StepError: Se a instalação falhar.
    """
    chroot_checked(
        ["pacman", "-S", "--needed", "--noconfirm", "networkmanager"],
        "não foi possível instalar o NetworkManager.",
    )

def _enable_networkmanager() -> None:
    """
    Habilita o serviço `NetworkManager.service` para iniciar automaticamente
    no boot do sistema instalado.

    :raises StepError: Se a habilitação falhar.
    """
    chroot_checked(
        ["systemctl", "enable", "NetworkManager.service"],
        "não foi possível habilitar o NetworkManager.",
    )

def run() -> None:
    """
    Instala e habilita o NetworkManager no sistema instalado.

    O processo é realizado em duas etapas independentes:

    1. `_install_networkmanager`: instala o pacote `networkmanager` via
       `pacman` no ambiente chroot, garantindo que a ferramenta de
       gerenciamento de rede esteja disponível.

    2. `_enable_networkmanager`: habilita o serviço `NetworkManager.service`
       via `systemctl` para que seja iniciado automaticamente no boot.

    Caso qualquer etapa falhe, um `StepError` é levantado informando o
    motivo da falha.
    """
    _install_networkmanager()
    _enable_networkmanager()
from common import chroot_checked

def _set_timezone() -> None:
    """
    Configura o fuso horário do sistema para `America/Bahia` criando
    um link simbólico de `/usr/share/zoneinfo/America/Bahia` para
    `/etc/localtime`.
    """
    chroot_checked(
        [
            "ln", "-sf",
            "/usr/share/zoneinfo/America/Bahia",
            "/etc/localtime",
        ],
        "não foi possível configurar o fuso horário.",
    )

def _sync_hardware_clock() -> None:
    """
    Sincroniza o relógio de hardware (RTC) com o horário do sistema
    usando `hwclock --systohc`.
    """
    chroot_checked(
        ["hwclock", "--systohc"],
        "não foi possível configurar o relógio de hardware.",
    )

def run() -> None:
    """
    Configura o fuso horário e o relógio de hardware do sistema instalado.

    O processo é realizado em duas etapas independentes:

    1. `_set_timezone`: cria um link simbólico de
       `/usr/share/zoneinfo/America/Bahia` para `/etc/localtime`,
       definindo o fuso horário do sistema.

    2. `_sync_hardware_clock`: executa `hwclock --systohc` para
       sincronizar o relógio de hardware (RTC) com o horário atual
       do sistema.

    Caso qualquer etapa falhe, um `StepError` é levantado informando
    o motivo da falha.
    """
    _set_timezone()
    _sync_hardware_clock()
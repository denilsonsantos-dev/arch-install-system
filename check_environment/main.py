from common import INSTALL_TARGET, StepError

def _validate_install_target() -> None:
    """
    Verifica se o alvo de instalação configurado é válido.
    """
    valid_targets = ("UEFI", "BIOS", "AMBOS")
    if INSTALL_TARGET not in valid_targets:
        raise StepError(f"alvo de instalação inválido: {INSTALL_TARGET}")

def _is_uefi_booted() -> bool:
    """
    Verifica se o sistema foi inicializado em modo UEFI 64-bit.

    :return: True se estiver em UEFI 64-bit, False caso contrário.
    """
    efi_path = "/sys/firmware/efi/fw_platform_size"
    try:
        with open(efi_path, "r", encoding="utf-8") as file:
            return file.read().strip() == "64"
    except OSError:
        return False

def _validate_boot_mode_compatibility(is_uefi: bool) -> None:
    """
    Valida se o modo de boot atual é compatível com o alvo de instalação.

    :param is_uefi: Indicador de se o sistema está em modo UEFI.
    """
    if INSTALL_TARGET == "UEFI" and not is_uefi:
        raise StepError("o script deve ser executado em UEFI 64-bit.")
    if INSTALL_TARGET == "BIOS" and is_uefi:
        raise StepError("o script deve ser executado em modo BIOS.")

def run() -> None:
    """
    Valida o alvo de instalação e a compatibilidade com o modo de boot do sistema.

    O processo é realizado em três etapas independentes:

    1. `_validate_install_target`: verifica se a variável `INSTALL_TARGET`
       possui um valor válido ("UEFI", "BIOS" ou "AMBOS").

    2. `_is_uefi_booted`: lê o arquivo `/sys/firmware/efi/fw_platform_size`
       para determinar se o sistema foi inicializado em modo UEFI 64-bit.

    3. `_validate_boot_mode_compatibility`: garante que o modo de boot
       detectado seja compatível com o `INSTALL_TARGET` especificado,
       levantando um erro se houver incompatibilidade (ex: tentar instalar
       em modo BIOS quando o sistema está em UEFI, ou vice-versa).

    Caso qualquer validação falhe, um `StepError` é levantado informando o motivo da falha.
    """
    _validate_install_target()
    is_uefi = _is_uefi_booted()
    _validate_boot_mode_compatibility(is_uefi)
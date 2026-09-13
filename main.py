from common import StepError

from check_environment.main import run as check_environment
from check_internet.main import run as check_internet
from configure_keyboard.main import run as configure_keyboard
from configure_locale.main import run as configure_locale
from configure_timezone.main import run as configure_timezone
from storage.main import prepare, reset as reset_target_installation
from mount_filesystems.main import run as mount_filesystems
from create_swapfile.main import run as create_swapfile
from activate_swapfile.main import run as activate_swapfile
from install_base_system.main import run as install_base_system
from generate_fstab.main import run as generate_fstab
from configure_installed_locale.main import run as configure_installed_locale
from configure_hostname.main import run as configure_hostname
from configure_installed_timezone.main import run as configure_installed_timezone
from configure_root_password.main import run as configure_root_password
from create_user.main import run as create_user
from configure_pacman.main import run as configure_pacman
from configure_sysctl.main import run as configure_sysctl
from configure_trim.main import run as configure_trim
from configure_kernel.main import run as configure_kernel
from configure_systemd_boot.main import run as configure_systemd_boot
from configure_aur_helper.main import run as configure_aur_helper
from configure_network.main import run as configure_network
from install_essentials_packages.main import run as install_nano

def build_steps():
    return [
        ("Checando ambiente", check_environment, None),
        ("Verificando internet", check_internet, None),
        ("Configurando teclado do ambiente live", configure_keyboard, None),
        ("Configurando locale do ambiente live", configure_locale, None),
        ("Configurando fuso horário do ambiente live", configure_timezone, None),
        ("Preparando e formatando o armazenamento", prepare, None),
        ("Montando os sistemas de arquivos", mount_filesystems, None),
        ("Criando swapfile", create_swapfile, None),
        ("Ativando swapfile", activate_swapfile, None),
        ("Instalando sistema base", install_base_system, None),
        ("Gerando fstab", generate_fstab, None),
        ("Configurando locale instalado", configure_installed_locale, None),
        ("Configurando hostname", configure_hostname, None),
        ("Configurando fuso horário instalado", configure_installed_timezone, None),
        ("Definindo senha do root", configure_root_password, None),
        ("Criando usuário", create_user, None),
        ("Configurando pacman", configure_pacman, None),
        ("Configurando sysctl", configure_sysctl, None),
        ("Habilitando TRIM na particao SSD do sistema", configure_trim, None),
        ("Configurando kernel do sistema", configure_kernel, None),
        ("Configurando bootloader", configure_systemd_boot, None),
        ("Configurando auxiliar AUR", configure_aur_helper, None),
        ("Configurando rede do sistema", configure_network, None),
        ("Instalando nano", install_nano, None),
    ]

def _execute_step(function, username):
    if function is create_user:
        return function()

    if function is configure_aur_helper:
        if not username:
            raise StepError("não há usuário disponível para configurar o paru.")
        function(username)
        return username

    function()
    return username

def _get_user_choice():
    print("[T]entar novamente / [R]einiciar instalação / [S]air")

    while True:
        choice = input("Escolha: ").strip().lower()

        if choice in ("t", "r", "s"):
            return choice

        print("Opção inválida. Escolha T, R ou S.")

def _reset_installation():
    try:
        print("\nLimpando somente a instalação-alvo...")
        reset_target_installation()
        print("Instalação-alvo limpa. Reiniciando a instalacao do comeco.")
        return True

    except StepError as error:
        print(f"ERRO durante a limpeza: {error}")
        return False

def _handle_step_error(error):
    print(f"\nERRO: {error}")

    choice = _get_user_choice()

    if choice == "t":
        return "retry"

    if choice == "s":
        return "exit"

    if _reset_installation():
        return "restart"

    return "exit"

def _execute_current_step(name, function, username):
    print(f"\n==> {name}")

    try:
        username = _execute_step(function, username)
        return True, username

    except StepError as error:
        action = _handle_step_error(error)
        return action, username

def run_installation():
    steps = build_steps()
    current_step = 0
    username = None

    while current_step < len(steps):
        name, function, _ = steps[current_step]
        result, username = _execute_current_step(name, function, username)

        if result is True:
            current_step += 1
            continue

        if result == "retry":
            continue

        if result == "restart":
            return True

        return False

    return None

def main():
    while True:
        restart = run_installation()

        if restart is None:
            print("\nConfiguração do sistema concluída!")
            return

        if restart is False:
            print("Instalação encerrada.")
            return

if __name__ == "__main__":
    main()
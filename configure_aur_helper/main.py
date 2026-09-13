from common import chroot_checked, run_command

def _install_paru_dependencies() -> None:
    """
    Instala as dependências necessárias para compilar o paru e configurar
    o sudo (`base-devel`, `git`, `sudo`) no sistema instalado.
    """
    chroot_checked(
        [
            "pacman", "-S",
            "--needed", "--noconfirm",
            "base-devel", "git",
        ],
        "não foi possível instalar as dependências do paru e sudo.",
    )

def _configure_wheel_sudo() -> None:
    """
    Configura o grupo `wheel` para executar comandos como superusuário
    sem senha, descomentando a regra correspondente no `/etc/sudoers`.
    """
    chroot_checked(
        [
            "sed", "-i",
            r"s/^# %wheel ALL=(ALL:ALL) NOPASSWD: ALL/%wheel ALL=(ALL:ALL) NOPASSWD: ALL/",
            "/etc/sudoers",
        ],
        "não foi possível configurar sudo para o grupo wheel.",
    )

def _clean_paru_directory(username: str) -> None:
    """
    Remove o diretório temporário do paru, se existir.

    :param username: Nome do usuário proprietário do diretório.
    """
    run_command(
        ["rm", "-rf", f"/home/{username}/paru"],
        "não foi possível remover os arquivos temporários do paru.",
    )

def _clone_paru_repository(username: str) -> None:
    """
    Clona o repositório do paru do AUR para o diretório do usuário.

    :param username: Nome do usuário que executará o clone.
    """
    chroot_checked(
        [
            "runuser", "-u", username, "--",
            "git", "clone",
            "https://aur.archlinux.org/paru.git",
            f"/home/{username}/paru",
        ],
        "não foi possível clonar o paru.",
    )

def _build_and_install_paru(username: str) -> None:
    """
    Compila e instala o pacote paru usando `makepkg` como o usuário
    especificado.

    :param username: Nome do usuário que executará a compilação.
    """
    chroot_checked(
        [
            "runuser", "-u", username, "--",
            "makepkg",
            "-D", f"/home/{username}/paru",
            "-sic",
            "--noconfirm",
        ],
        "não foi possível compilar e instalar o paru.",
    )

def run(username: str) -> None:
    """
    Instala o gerenciador de pacotes AUR `paru` e configura privilégios
    de sudo para o grupo wheel no sistema instalado.

    O processo é realizado em seis etapas independentes:

    1. `_install_paru_dependencies`: instala as dependências necessárias
       (`base-devel` e `git`) via pacman.

    2. `_configure_wheel_sudo`: descomenta a regra do grupo `wheel` no
       `/etc/sudoers` para permitir execução sem senha.

    3. `_clean_paru_directory`: remove qualquer diretório temporário
       pré-existente do paru.

    4. `_clone_paru_repository`: clona o repositório do paru do AUR
       para o diretório do usuário.

    5. `_build_and_install_paru`: compila e instala o paru usando
       `makepkg` com privilégios de usuário normal.

    6. `_clean_paru_directory`: remove os arquivos temporários após
       a instalação.

    Caso qualquer etapa falhe, um `StepError` é levantado informando
    o motivo da falha.
    """
    _install_paru_dependencies()
    _configure_wheel_sudo()
    _clean_paru_directory(username)
    _clone_paru_repository(username)
    _build_and_install_paru(username)
    _clean_paru_directory(username)
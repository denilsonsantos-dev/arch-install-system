# Instalador Arch Linux modularizado

Execute a partir da raiz:

    sudo python3 main.py

Cada etapa possui sua própria pasta e `main.py`. O arquivo `common.py`
contém somente infraestrutura compartilhada entre etapas.

Estrutura:

arch-install-system/
├── main.py
├── common.py
├── check_environment/
├── check_internet/
├── configure_keyboard/
├── configure_locale/
├── configure_timezone/
├── storage/
├── mount_filesystems/
├── create_swapfile/
├── activate_swapfile/
├── install_base_system/
├── generate_fstab/
├── configure_installed_locale/
├── configure_hostname/
├── configure_installed_timezone/
├── configure_root_password/
├── configure_sudo/
├── create_user/
├── configure_pacman/
├── configure_sysctl/
├── configure_trim/
├── configure_kernel/
├── configure_systemd_boot/
├── configure_aur_helper/
├── configure_network/
├── install_nano/

As pastas de etapa possuem também `__init__.py` para serem pacotes Python.
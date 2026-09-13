INSTALL_TARGET = "UEFI"

# CONFIGURAÇÕES DE DISCO
DISK = "/dev/vda"
DISK_WITH_PARTITION_SUFIX = f"{DISK}"

ESP_LABEL = "BOOTLOADER"
ESP_PARTITION = f"{DISK_WITH_PARTITION_SUFIX}1" # Partição utilizada como bootloader
ESP_SIZE = "1G"

ROOT_LABEL = "ArchTempOS"
ROOT_PARTITION = f"{DISK_WITH_PARTITION_SUFIX}2" # Partição utilizada pela instalação temporária
ROOT_SIZE = "8G"

# CONFIGURAÇÕES DE DISCO (PARA PARTICIONAMENTO)
ARCHOS_LABEL = "ArchOS"
ARCHOS_PARTITION = f"{DISK_WITH_PARTITION_SUFIX}3"
ARCHOS_SIZE = "0"

# CONFIGURACOES PARA O KERNEL E BOOTLOADER
UKI_PATH = "/efi/EFI/Linux/arch-temp-linux-zen.efi" # Caminho aonde a imagem unificada do kernel ficara armazenada
SYSTEMD_BOOT_ENTRY = "arch-temp.conf" # Nome do arquivo configurando a entrada do sistema no menu
SYSTEMD_BOOT_TITLE = "Arch Linux [TEMP]" # Nome do sistema no menu de selecao de sistema

# CONFIGURAÇOES DE SWAP
SWAPFILE = "/mnt/swapfile"
SWAP_SIZE_MB = 512
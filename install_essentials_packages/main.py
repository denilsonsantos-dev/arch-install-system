from common import chroot_checked


def run():
    chroot_checked(["pacman", "-S", "--needed", "--noconfirm",
        "nano",
    ],
    "não foi possível instalar todos os pacotes essenciais.")
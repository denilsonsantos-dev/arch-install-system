from common import chroot_checked


def run():
    chroot_checked(
        ["passwd"],
        "não foi possível definir a senha do root.",
        interactive=True,
    )
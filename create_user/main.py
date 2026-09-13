from common import chroot_checked

def _create_user(username):
    chroot_checked(
        ["useradd", "-m", "-G", "wheel", username],
        "não foi possível criar o usuário.",
    )

def _set_password(username):
    chroot_checked(
        ["passwd", username],
        "não foi possível definir a senha do usuário.",
        interactive=True,
    )

def run():
    while True:
        username = input("Nome do primeiro usuário: ").strip()

        if username:
            break

        print("ERRO: o nome do usuário não pode ser vazio.")

    _create_user(username)
    _set_password(username)

    return username
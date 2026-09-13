from common import chroot_checked


def run():
    """
    Habilita o TRIM contínuo para a partição raiz do sistema instalado.

    O processo é realizado em três etapas:

    1. Executa o comando dentro do sistema instalado usando `chroot_checked`.
       A função `chroot_checked` garante que o comando seja executado no
       ambiente do sistema que está sendo instalado e verifica se houve erro.

    2. O comando `sed` modifica o arquivo `/etc/fstab`:
       - `-i` faz a alteração diretamente no arquivo.
       - `-E` habilita expressões regulares estendidas.
       - A primeira expressão procura uma entrada que monte `/` usando
         o sistema de arquivos `ext4`.
       - A segunda expressão localiza a opção `rw` nessa entrada e adiciona
         `,discard` imediatamente depois dela.

       Por exemplo:

           /   ext4   rw,relatime   0 1

       torna-se:

           /   ext4   rw,discard,relatime   0 1

       A opção `discard` habilita o envio contínuo de comandos TRIM ao SSD
       quando blocos deixam de ser utilizados.

    3. Caso o `sed` falhe, `chroot_checked` interrompe o processo e exibe
       a mensagem informando que não foi possível habilitar o TRIM.

    Em resumo, a função localiza a entrada da partição raiz ext4 no
    `/etc/fstab` e adiciona a opção `discard` às opções de montagem.
    """
    chroot_checked(
        [
            "sed", "-i", "-E",
            r"/[[:space:]]\/[[:space:]]+ext4[[:space:]]/"
            r"s/([[:space:]]rw[^[:space:]]*)/\1,discard/",
            "/etc/fstab",
        ],
        "não foi possível habilitar o TRIM no SSD via fstab.",
    )
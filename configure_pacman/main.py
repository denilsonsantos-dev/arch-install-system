from common import StepError, chroot_checked


def _enable_color() -> None:
    """
    Ativa a saída colorida no `pacman.conf` dentro do sistema instalado.
    """
    chroot_checked(
        ["sed", "-i", "-E", "s/^#Color$/Color/", "/etc/pacman.conf"],
        "não foi possível ativar Color no pacman.conf.",
    )


def _enable_parallel_downloads() -> None:
    """
    Ativa os downloads paralelos (fixados em 10) no `pacman.conf`
    dentro do sistema instalado.
    """
    chroot_checked(
        [
            "sed", "-i", "-E",
            "s/^#ParallelDownloads = [0-9]+$/ParallelDownloads = 10/",
            "/etc/pacman.conf",
        ],
        "não foi possível ativar ParallelDownloads no pacman.conf.",
    )


def _read_pacman_conf(pacman_conf: str) -> list[str]:
    """
    Lê todas as linhas do arquivo `pacman.conf`.

    :param pacman_conf: Caminho absoluto do arquivo.
    :return: Lista de linhas do arquivo.
    """
    try:
        with open(pacman_conf, "r", encoding="utf-8") as file:
            return file.readlines()
    except OSError as error:
        raise StepError(f"não foi possível ler o pacman.conf: {error}") from error


def _write_pacman_conf(pacman_conf: str, content: list[str]) -> None:
    """
    Sobrescreve o arquivo `pacman.conf` com o conteúdo fornecido.

    :param pacman_conf: Caminho absoluto do arquivo.
    :param content: Lista de linhas a serem escritas.
    """
    try:
        with open(pacman_conf, "w", encoding="utf-8") as file:
            file.writelines(content)
    except OSError as error:
        raise StepError(f"não foi possível escrever no pacman.conf: {error}") from error


def _find_options_section(content: list[str]) -> int:
    """
    Localiza o índice da seção `[options]` no conteúdo do `pacman.conf`.

    :param content: Lista de linhas do arquivo.
    :return: Índice da linha `[options]`.
    :raises StepError: Se a seção não for encontrada.
    """
    for i, line in enumerate(content):
        if line.strip() == "[options]":
            return i
    raise StepError("seção [options] não encontrada no pacman.conf.")


def _has_option(content: list[str], option: str) -> bool:
    """
    Verifica se uma opção específica já existe no conteúdo do `pacman.conf`.

    :param content: Lista de linhas do arquivo.
    :param option: Nome da opção a ser verificada.
    :return: True se a opção existir, False caso contrário.
    """
    return any(line.strip() == option for line in content)


def _insert_option_after_section(content: list[str], section_index: int, option: str) -> list[str]:
    """
    Insere uma opção imediatamente após uma seção específica.

    :param content: Lista de linhas do arquivo.
    :param section_index: Índice da seção após a qual inserir.
    :param option: Opção a ser inserida.
    :return: Nova lista de linhas com a opção inserida.
    """
    new_content = content.copy()
    new_content.insert(section_index + 1, f"{option}\n")
    return new_content


def _add_ilovecandy(pacman_conf: str) -> None:
    """
    Garante que a opção `ILoveCandy` esteja presente na seção `[options]`
    do `pacman.conf` no sistema hospedeiro.

    :param pacman_conf: Caminho absoluto do arquivo `pacman.conf` no host.
    """
    content = _read_pacman_conf(pacman_conf)

    if _has_option(content, "ILoveCandy"):
        return

    options_index = _find_options_section(content)
    new_content = _insert_option_after_section(content, options_index, "ILoveCandy")
    _write_pacman_conf(pacman_conf, new_content)


def run() -> None:
    """
    Configura opções de interface, desempenho e o Easter egg `ILoveCandy`
    do `pacman` no sistema instalado.

    O processo é realizado em três etapas independentes:

    1. `_enable_color`: usa `sed` via `chroot_checked` para descomentar
       a diretiva `Color` no `/etc/pacman.conf` do ambiente instalado,
       ativando a saída colorida.

    2. `_enable_parallel_downloads`: usa `sed` via `chroot_checked` para
       descomentar e configurar `ParallelDownloads = 10` no
       `/etc/pacman.conf` do ambiente instalado.

    3. `_add_ilovecandy`: manipula diretamente o arquivo
       `/mnt/etc/pacman.conf` no sistema hospedeiro para garantir que a
       opção `ILoveCandy` esteja presente logo após a seção `[options]`.

    Caso qualquer etapa falhe, um `StepError` é levantado informando o
    motivo da falha.
    """
    _enable_color()
    _enable_parallel_downloads()
    _add_ilovecandy("/mnt/etc/pacman.conf")
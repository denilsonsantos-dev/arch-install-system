import os
from common import require_success, run_command

def _uncomment_locale() -> None:
    """
    Descomenta o locale `pt_BR.UTF-8 UTF-8` no arquivo `/etc/locale.gen`.
    """
    result = run_command([
        "sed", "-i",
        "s/^#pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/",
        "/etc/locale.gen",
    ])
    require_success(result, "não foi possível configurar o locale.")

def _generate_locales() -> None:
    """
    Executa `locale-gen` para gerar os locales configurados no sistema.
    """
    result = run_command(["locale-gen"])
    require_success(result, "não foi possível gerar o locale.")

def _set_lang_environment() -> None:
    """
    Define a variável de ambiente `LANG` como `pt_BR.UTF-8` para o
    processo atual.
    """
    os.environ["LANG"] = "pt_BR.UTF-8"

def run() -> None:
    """
    Configura o locale do sistema para `pt_BR.UTF-8`.

    O processo é realizado em três etapas independentes:

    1. `_uncomment_locale`: descomenta a linha do locale brasileiro no
       arquivo `/etc/locale.gen` usando `sed`.

    2. `_generate_locales`: executa `locale-gen` para compilar os locales
       configurados.

    3. `_set_lang_environment`: define a variável de ambiente `LANG` como
       `pt_BR.UTF-8` para o processo atual.

    Caso qualquer etapa falhe, um erro é levantado informando o motivo
    da falha.
    """
    _uncomment_locale()
    _generate_locales()
    _set_lang_environment()
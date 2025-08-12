#!/usr/bin/env python3
"""Cross-platform helper script to manage Docker commands for the project."""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import List


def _color(code: str, msg: str) -> str:
    return f"\033[{code}m{msg}\033[0m"


def print_header(msg: str) -> None:
    print(_color("0;34", f"=== {msg} ==="))


def print_success(msg: str) -> None:
    print(_color("0;32", f"✅ {msg}"))


def print_error(msg: str) -> None:
    print(_color("0;31", f"❌ {msg}"))


def check_docker() -> List[str]:
    """Ensure Docker and Docker Compose are available.

    Returns the docker compose command as a list.
    """
    if not shutil.which("docker"):
        print_error("Docker não está instalado!")
        print("Por favor, instale o Docker primeiro:")
        print("https://docs.docker.com/get-docker/")
        sys.exit(1)

    if shutil.which("docker-compose"):
        return ["docker-compose"]
    result = subprocess.run(
        ["docker", "compose", "version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        return ["docker", "compose"]

    print_error("Docker Compose não está instalado!")
    print("Por favor, instale o Docker Compose primeiro:")
    print("https://docs.docker.com/compose/install/")
    sys.exit(1)


def build_image(dc: List[str]) -> None:
    print_header("Construindo imagem Docker")
    subprocess.check_call(dc + ["build"])
    print_success("Imagem construída com sucesso!")


def run_generator(dc: List[str]) -> None:
    print_header("Executando gerador de currículos")
    subprocess.check_call(dc + [
        "run",
        "--rm",
        "resume-generator",
        "python3",
        "scripts/main.py",
    ])
    print_success("Geração de currículos concluída!")
    print("Os arquivos foram gerados na pasta 'outputs/'")


def run_custom(dc: List[str], args: List[str]) -> None:
    print_header(f"Executando comando customizado: {' '.join(args)}")
    subprocess.check_call(dc + ["run", "--rm", "resume-generator"] + args)


def run_shell(dc: List[str]) -> None:
    print_header("Abrindo shell interativo no container")
    subprocess.check_call(dc + ["run", "--rm", "resume-generator", "bash"])


def clean(dc: List[str]) -> None:
    print_header("Limpando containers e imagens Docker")
    subprocess.call(dc + [
        "down",
        "--rmi",
        "all",
        "--volumes",
        "--remove-orphans",
    ])
    subprocess.call(["docker", "system", "prune", "-f"])
    print_success("Limpeza concluída!")


def logs(dc: List[str]) -> None:
    print_header("Mostrando logs do container")
    subprocess.check_call(dc + ["logs", "-f", "resume-generator"])


def show_help() -> None:
    print("🐳 Script Docker para Gerador de Currículos")
    print()
    print("COMANDOS DISPONÍVEIS:")
    print("  build     - Constrói a imagem Docker")
    print("  run       - Executa o gerador de currículos")
    print("  shell     - Abre shell interativo no container")
    print("  clean     - Remove containers e imagens Docker")
    print("  logs      - Mostra logs do container")
    print("  help      - Mostra esta ajuda")
    print()
    print("EXEMPLOS:")
    print("  python docker_run.py build")
    print("  python docker_run.py run")
    print()
    print("COMANDOS CUSTOMIZADOS:")
    print("  python docker_run.py python3 scripts/main.py")
    print("  python docker_run.py python3 scripts/scrape_jobs.py")


def main(argv: List[str]) -> None:
    dc = check_docker()
    cmd = argv[1] if len(argv) > 1 else "help"

    if cmd == "build":
        build_image(dc)
    elif cmd == "run":
        run_generator(dc)
    elif cmd == "shell":
        run_shell(dc)
    elif cmd == "clean":
        clean(dc)
    elif cmd == "logs":
        logs(dc)
    elif cmd in {"help", "--help", "-h"}:
        show_help()
    else:
        run_custom(dc, argv[1:])


if __name__ == "__main__":
    main(sys.argv)

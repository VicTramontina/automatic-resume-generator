#!/bin/bash

# Script para facilitar o uso do projeto com Docker
# Este script elimina a necessidade de instalar dependências localmente

set -e

DOCKER_IMAGE="curriculo-generator"
CONTAINER_NAME="curriculo-container"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para verificar se Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado!"
        echo "Por favor, instale o Docker primeiro:"
        echo "https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Verificar Docker Compose (versão nova ou antiga)
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose não está instalado!"
        echo "Por favor, instale o Docker Compose primeiro:"
        echo "https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Função para construir a imagem Docker
build_image() {
    print_header "Construindo imagem Docker"
    $DOCKER_COMPOSE_CMD build
    print_success "Imagem construída com sucesso!"
}

# Função para executar o gerador de currículos
run_generator() {
    print_header "Executando gerador de currículos"
    $DOCKER_COMPOSE_CMD run --rm resume-generator python3 scripts/main.py
    print_success "Geração de currículos concluída!"
    echo "Os arquivos foram gerados na pasta 'outputs/'"
}

# Função para executar comandos customizados
run_custom() {
    print_header "Executando comando customizado: $*"
    $DOCKER_COMPOSE_CMD run --rm resume-generator "$@"
}

# Função para abrir shell interativo
run_shell() {
    print_header "Abrindo shell interativo no container"
    $DOCKER_COMPOSE_CMD run --rm resume-generator bash
}

# Função para limpar containers e imagens
clean() {
    print_header "Limpando containers e imagens Docker"
    $DOCKER_COMPOSE_CMD down --rmi all --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    print_success "Limpeza concluída!"
}

# Função para mostrar logs
logs() {
    print_header "Mostrando logs do container"
    $DOCKER_COMPOSE_CMD logs -f resume-generator
}

# Função para mostrar ajuda
show_help() {
    echo "🐳 Script Docker para Gerador de Currículos"
    echo ""
    echo "COMANDOS DISPONÍVEIS:"
    echo "  build     - Constrói a imagem Docker"
    echo "  run       - Executa o gerador de currículos"
    echo "  shell     - Abre shell interativo no container"
    echo "  clean     - Remove containers e imagens Docker"
    echo "  logs      - Mostra logs do container"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo "EXEMPLOS:"
    echo "  ./docker-run.sh build"
    echo "  ./docker-run.sh run"
    echo "  ./docker-run.sh shell"
    echo ""
    echo "COMANDOS CUSTOMIZADOS:"
    echo "  ./docker-run.sh python3 scripts/main.py"
    echo "  ./docker-run.sh python3 scripts/scrape_jobs.py"
}

# Main
main() {
    check_docker

    case "${1:-help}" in
        "build")
            build_image
            ;;
        "run")
            run_generator
            ;;
        "shell")
            run_shell
            ;;
        "clean")
            clean
            ;;
        "logs")
            logs
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            if [ $# -eq 0 ]; then
                show_help
            else
                run_custom "$@"
            fi
            ;;
    esac
}

main "$@"

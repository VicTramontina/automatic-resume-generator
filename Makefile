.PHONY: build run shell clean help

# Comandos Docker
.RECIPEPREFIX := >
PYTHON := $(shell command -v python3 >/dev/null 2>&1 && echo python3 || echo python)

build:
> @echo "🐳 Construindo imagem Docker..."
> $(PYTHON) docker_run.py build

run:
> @echo "🚀 Executando gerador de currículos com Docker..."
> $(PYTHON) docker_run.py run

shell:
> @echo "🐚 Abrindo shell interativo no container..."
> $(PYTHON) docker_run.py shell

clean:
> @echo "🧹 Limpando containers e imagens Docker..."
> $(PYTHON) docker_run.py clean

# Comando padrão
all: run

# Ajuda
help:
> @echo "📋 Gerador de Currículos - Comandos Docker"
> @echo ""
> @echo "COMANDOS DISPONÍVEIS:"
> @echo "  make build   - Constrói a imagem Docker"
> @echo "  make run     - Executa o gerador de currículos"
> @echo "  make shell   - Abre shell interativo no container"
> @echo "  make clean   - Remove containers e imagens Docker"
> @echo "  make help    - Mostra esta ajuda"
> @echo ""
> @echo "EXEMPLO DE USO:"
> @echo "  make build && make run"
> @echo ""
> @echo "Para comandos avançados: $(PYTHON) docker_run.py help"
> @echo ""
> @echo "🐳 Este projeto usa exclusivamente Docker para eliminar"
> @echo "   problemas de dependências entre sistemas operacionais."

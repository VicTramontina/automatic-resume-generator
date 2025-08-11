.PHONY: build run shell clean help

# Comandos Docker
build:
	@echo "🐳 Construindo imagem Docker..."
	./docker-run.sh build

run:
	@echo "🚀 Executando gerador de currículos com Docker..."
	./docker-run.sh run

shell:
	@echo "🐚 Abrindo shell interativo no container..."
	./docker-run.sh shell

clean:
	@echo "🧹 Limpando containers e imagens Docker..."
	./docker-run.sh clean

# Comando padrão
all: run

# Ajuda
help:
	@echo "📋 Gerador de Currículos - Comandos Docker"
	@echo ""
	@echo "COMANDOS DISPONÍVEIS:"
	@echo "  make build   - Constrói a imagem Docker"
	@echo "  make run     - Executa o gerador de currículos"
	@echo "  make shell   - Abre shell interativo no container"
	@echo "  make clean   - Remove containers e imagens Docker"
	@echo "  make help    - Mostra esta ajuda"
	@echo ""
	@echo "EXEMPLO DE USO:"
	@echo "  make build && make run"
	@echo ""
	@echo "Para comandos avançados: ./docker-run.sh help"
	@echo ""
	@echo "🐳 Este projeto usa exclusivamente Docker para eliminar"
	@echo "   problemas de dependências entre sistemas operacionais."

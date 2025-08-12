# Currículo Automático

Este projeto automatiza a busca de vagas remotas, a personalização de um currículo em LaTeX e a geração de PDFs específicos para cada vaga encontrada. 

**🐳 Projeto 100% Dockerizado** - Não requer instalação de dependências locais!

## Fluxo do Sistema

1. **Coletar vagas** definidas em `config/job_config.yaml`
2. **Analisar** cada vaga com a API do Gemini para adaptar o currículo
3. **Gerar saída** em `outputs/` contendo um resumo (`job.md`) e o PDF do currículo ajustado

## 🚀 Uso Rápido

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Configuração Inicial
```bash
# Configure sua API key do Gemini (funciona em Linux, macOS e Windows)
echo GEMINI_API_KEY=sua_chave_aqui > .env
```

### Execução
```bash
# Construa e execute
make build && make run

# Ou comandos separados
make build   # Constrói a imagem Docker
make run     # Executa o gerador de currículos
```

## 📋 Comandos Disponíveis

```bash
make build   # Constrói a imagem Docker
make run     # Executa o gerador de currículos
make shell   # Abre shell interativo no container
make clean   # Remove containers e imagens Docker
make help    # Mostra ajuda
```

## 🎯 Configuração

### API do Gemini
1. Obtenha uma chave em [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie um arquivo `.env` na raiz do projeto com o conteúdo:
   ```bash
   GEMINI_API_KEY=sua_chave_aqui
   ```

### Configuração de Vagas
Edite `config/job_config.yaml` para definir os sites e critérios de busca.

## 📁 Estrutura do Projeto

```
├── config/             # Configurações
├── latex/             # Modelo do currículo em LaTeX
├── outputs/           # PDFs e resumos gerados
├── scripts/           # Scripts Python
├── Dockerfile         # Definição da imagem Docker
├── docker-compose.yml # Configuração Docker Compose
└── docker_run.py      # Script conveniente
```

## ✨ Funcionalidades

- **Web Scraping Avançado**: Paginação, extração detalhada de vagas
- **Personalização IA**: Usa Gemini para adaptar currículos
- **Geração PDF**: Compilação automática com LaTeX
- **Ambiente Isolado**: Docker elimina problemas de dependências

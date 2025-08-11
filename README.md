# Currículo Automático

Este projeto automatiza a busca de vagas remotas, a personalização de um currículo em LaTeX e a geração de PDFs específicos para cada vaga encontrada. O fluxo geral é:

1. **Coletar vagas** definidas em `config/job_config.yaml`.
2. **Analisar** cada vaga com a API do Gemini para adaptar o currículo.
3. **Gerar saída** em `outputs/` contendo um resumo (`job.md`) e o PDF do currículo ajustado para cada vaga.

## Organização do projeto

```
├── config/          # Arquivos de configuração
│   └── job_config.yaml
├── latex/           # Modelo base do currículo em LaTeX
├── outputs/         # Resultados gerados (um diretório por vaga)
├── scripts/         # Scripts Python de automação
└── Makefile         # Alvos para instalação, lint e execução
```

## Usando o Makefile

```bash
make setup   # cria ambiente virtual e instala dependências
make lint    # verifica sintaxe dos scripts Python
make run     # roda a pipeline completa
make clean   # remove ambiente virtual e saídas geradas
```

Para personalizar o currículo, defina a variável de ambiente `GEMINI_API_KEY` com sua chave da API do Gemini antes de executar `make run`.

## Configuração das vagas (`job_config.yaml`)

O arquivo `config/job_config.yaml` controla tanto o que será buscado quanto os filtros aplicados às vagas. Os principais parâmetros são:

- `skills`: lista de palavras-chave que devem aparecer na vaga. Se nenhuma estiver presente, a vaga é ignorada.
- `salary`:
  - `usd`: salário mínimo em dólares (USD).
  - `brl`: salário mínimo em reais (BRL).
- `sites`: lista de sites a serem raspados. Cada site contém:
  - `name`: nome do site.
  - `url`: endereço da página de vagas.
  - `job_selector`: seletor CSS que identifica cada card de vaga na página.
  - `fields`: mapeamento de campos desejados para seletores CSS relativos ao card:
    - `title`
    - `company`
    - `description`
    - `salary`
    - `skills`

Adapte estes campos conforme a estrutura HTML do site que deseja consultar.

## Saídas

Para cada vaga aprovada pelos filtros, é criado um diretório `outputs/job_N/` contendo:

- `job.md`: resumo em Markdown com os dados coletados.
- `resume.tex`: currículo ajustado em LaTeX.
- `resume.pdf`: currículo compilado.

Assim, você obtém um PDF personalizado para cada vaga remota filtrada.


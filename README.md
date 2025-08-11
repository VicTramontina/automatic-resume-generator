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

## Funcionalidades Avançadas de Web Scraping

### 1. Extração de Páginas Individuais de Vagas

O sistema agora pode seguir links das vagas para extrair informações mais detalhadas das páginas individuais.

### 2. Navegação por Páginas (Paginação)

O sistema suporta três tipos de paginação:

- **`next_button`**: Segue botões "próxima página" até não existir mais
- **`numbered_links`**: Extrai links numerados de paginação  
- **`url_pattern`**: Gera URLs baseado em um padrão (ex: `?page={page}`)

### 3. Melhorias de Robustez

- Headers de User-Agent realistas para evitar bloqueios
- Tratamento de erros que permite continuar mesmo se algumas páginas falharem
- Logs detalhados do progresso do scraping
- Rate limiting automático entre requisições (1s entre páginas, 0.5s entre vagas)

## Configuração das vagas (`job_config.yaml`)

O arquivo `config/job_config.yaml` controla tanto o que será buscado quanto os filtros aplicados às vagas. Os principais parâmetros são:

- `skills`: lista de habilidades com opções de obrigatórias ou opcionais
- `salary`:
  - `usd`: salário mínimo em dólares (USD).
  - `brl`: salário mínimo em reais (BRL).
- `sites`: lista de sites a serem raspados. Cada site contém:
  - `name`: nome do site.
  - `url`: endereço da página de vagas.
  - `job_selector`: seletor CSS que identifica cada card de vaga na página.
  - `max_jobs`: **NOVO** - número máximo de vagas qualificadas a coletar deste site
  - `fields`: mapeamento de campos desejados para seletores CSS relativos ao card:
    - `title`: título da vaga
    - `company`: nome da empresa
    - `link`: **OBRIGATÓRIO** - link para a página individual da vaga
  - `detail_fields`: campos extraídos da página individual da vaga:
    - `description`: descrição completa
    - `salary`: informações de salário
    - `skills`: tecnologias/habilidades
    - `requirements`: requisitos
    - `benefits`: benefícios
  - `pagination`: configuração para navegar por múltiplas páginas:
    - `type`: tipo de paginação (`next_button`, `numbered_links`, ou `url_pattern`)
    - Para `next_button`: `next_selector` (seletor do botão próxima)
    - Para `numbered_links`: `links_selector` (seletor dos links de página)
    - Para `url_pattern`: `url_pattern` (padrão da URL com `{page}`)

### Configuração de Skills (Obrigatórias vs Opcionais)

Agora você pode definir skills como obrigatórias ou opcionais:

```yaml
skills:
  # Skills obrigatórias - DEVEM estar presentes na vaga
  - name: "Python"
    required: true
  - name: "SQL" 
    required: true
  
  # Skills opcionais - se presentes, a vaga é aceita
  - name: "Docker"
    required: false
  - name: "JavaScript"
    required: false
  
  # Formato antigo ainda funciona (tratado como opcional)
  - "Git"
  - "Linux"
```

**Lógica de Filtragem:**
- Se uma vaga NÃO contém uma skill obrigatória (`required: true`), ela é rejeitada
- Se uma vaga contém pelo menos uma skill obrigatória E/OU uma skill opcional, ela é aceita
- O formato antigo (apenas string) continua funcionando como skill opcional

### Limite por Número de Vagas (ao invés de páginas)

Agora você define quantas vagas qualificadas quer de cada site:

```yaml
sites:
  - name: LinkedIn
    max_jobs: 15  # Para quando encontrar 15 vagas que atendam os critérios
    # ... outras configurações
```

**Como funciona:**
- O sistema navega pelas páginas até encontrar o número especificado de vagas que passem nos filtros
- Para automaticamente quando atinge `max_jobs` vagas qualificadas
- Há um limite de segurança de 20 páginas para evitar loops infinitos

### Exemplo de Configuração Completa

```yaml
skills:
  # Skills obrigatórias
  - name: "Python" 
    required: true
  - name: "SQL"
    required: true
  
  # Skills opcionais
  - name: "Docker"
    required: false
  - name: "React"
    required: false

salary:
  usd: 3000
  brl: 6000

sites:
  - name: "LinkedIn"
    url: "https://www.linkedin.com/jobs/search/?keywords=desenvolvedor"
    job_selector: ".job-search-card"
    max_jobs: 20  # Coleta até 20 vagas qualificadas
    
    fields:
      title: ".base-search-card__title"
      company: ".base-search-card__subtitle"
      link: ".base-card__full-link"
    
    detail_fields:
      description: ".description__text"
      skills: ".job-criteria__text"
    
    pagination:
      type: "numbered_links" 
      links_selector: ".pagination a"
```

### Tipos de Paginação

#### Botão "Próxima"
```yaml
pagination:
  type: "next_button"
  next_selector: ".pagination .next"
  max_pages: 5
```

#### Links Numerados
```yaml
pagination:
  type: "numbered_links"
  links_selector: ".pagination a"
  max_pages: 10
```

#### Padrão de URL
```yaml
pagination:
  type: "url_pattern"
  url_pattern: "https://site.com/jobs?page={page}"
  max_pages: 5
```

Adapte estes campos conforme a estrutura HTML do site que deseja consultar.

## Saídas

Para cada vaga aprovada pelos filtros, é criado um diretório `outputs/job_N/` contendo:

- `job.md`: resumo em Markdown com os dados coletados.
- `resume.tex`: currículo ajustado em LaTeX.
- `resume.pdf`: currículo compilado.

Assim, você obtém um PDF personalizado para cada vaga remota filtrada.

## Logs e Monitoramento

O sistema fornece logs detalhados durante a execução:

```
Scraping Remotar...
Found 2 additional pages to scrape
Scraping page: https://remotar.com.br/search/jobs?q=desenvolvedor
Found 10 job listings on this page
Scraping details for: Desenvolvedor Python Sênior
Scraping details for: Desenvolvedor Frontend React
...
Total jobs found: 25
```

## Dicas para Configuração

1. **Teste os seletores**: Use as ferramentas de desenvolvedor do navegador para testar os seletores CSS
2. **URLs relativas**: O sistema automaticamente converte URLs relativas em absolutas
3. **Campos opcionais**: Se um campo não for encontrado, será definido como `None`
4. **Paginação cautelosa**: Comece com `max_pages` baixo para testar
5. **Rate limiting**: O sistema já inclui delays automáticos para ser respeitoso com os servidores

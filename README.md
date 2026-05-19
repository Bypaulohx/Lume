# 🔒 Lume V2.0

**Ferramenta Profissional de Análise de Segurança Web**

*Do latim: iluminar falhas escondidas*

---

## O que é Lume?

Lume V2.0 é uma ferramenta de segurança avançada que vai muito além de scanners básicos. Ela fornece:

- ✅ **Análise Comportamental**: Reconhecimento dinâmico com Playwright
- ✅ **Escaneamento de Infraestrutura**: Port scanning com nmap e descoberta de subdomínios
- ✅ **Testes de Vulnerabilidade OWASP**: XSS, SQLi, Command Injection, Headers
- ✅ **Análise TLS/SSL**: Verificação de certificados e protocolos
- ✅ **Relatórios Profissionais**: HTML, PDF e JSON com recomendações de remediação
- ✅ **Operações Paralelas**: Multi-threading/Asyncio para máxima eficiência
- ✅ **Detecção de WAF**: Evita bloqueios desnecessários

> ⚠️ **Uso Ético**: Utilize **apenas** em sistemas com autorização explícita.

---

## O que mudou na V2.0?

### De V1 para V2

| Aspecto | V1 | V2 |
|--------|----|----|
| **Engine** | requests + BeautifulSoup | Playwright + nmap + sslyze |
| **Reconhecimento** | Apenas web | Port scanning + DNS + Subdomínios |
| **Análise** | Superficial (regex) | Comportamental + Infraestrutura |
| **Relatórios** | JSON/Markdown simples | HTML elegante + PDF + JSON estruturado |
| **Performance** | Sequencial | Assíncrono paralelo |
| **Cobertura** | 3 vulnerabilidades | +10 tipos de vulnerabilidades |
| **Remediação** | Não | Sim (explicações práticas) |

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                   Lume V2.0 CLI                          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬─────────────┐
        │            │            │             │
   ┌────▼──────┐ ┌──▼─────┐ ┌──▼────────┐ ┌──▼──┐
   │Recon      │ │Browser │ │Security   │ │SSL  │
   │Engine     │ │Engine  │ │Engine     │ │TLS  │
   │           │ │        │ │           │ │     │
   │ • nmap    │ │• Crawl │ │• XSS      │ │• Cert│
   │ • DNS     │ │• Forms │ │• SQLi     │ │• TLS │
   │ • Subs    │ │• JS    │ │• Hdrs     │ │• Vuln│
   └────┬──────┘ └──┬─────┘ └──┬────────┘ └──┬──┘
        │           │           │            │
        └───────────┼───────────┼────────────┘
                    │           │
            ┌───────▼───────────▼──────┐
            │  Report Builder           │
            │  (Jinja2 Templates)       │
            └───────┬────────────┬──────┘
                    │            │
            ┌───────▼──┐  ┌──────▼────┐
            │HTML      │  │PDF/JSON   │
            │Report    │  │Export     │
            └──────────┘  └───────────┘
```

## Estrutura do Projeto

- `backend/`
  - `api/` - rotas FastAPI e endpoints de varredura
  - `core/` - motores de varredura dinâmicos e de segurança
  - `reports/` - modelos e artefatos de relatório
- `frontend/` - interface React + Vite
- `lume/` - pacote principal com engines e utilitários

---

## Requisitos

### Sistema

- **Python 3.9+**
- **nmap** (para port scanning)
- **wkhtmltopdf** (para geração de PDF, opcional)

### Instalação de Dependências do Sistema

#### Windows (PowerShell - Admin)

```powershell
# Instalar Chocolatey (se não tiver)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm https://community.chocolatey.org/install.ps1 | iex

# Instalar ferramentas
choco install nmap -y
choco install wkhtmltopdf -y

# Instalar Playwright browsers
playwright install chromium
```

#### macOS

```bash
# Usar Homebrew
brew install nmap
brew install --cask wkhtmltopdf

# Instalar Playwright
playwright install chromium
```

#### Linux (Ubuntu/Debian)

```bash
# Instalar ferramentas
sudo apt-get update
sudo apt-get install -y nmap wkhtmltopdf

# Instalar dependências do Playwright
sudo apt-get install -y chromium-browser

# Instalar Playwright
playwright install chromium
```

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/lume.git
cd lume
```

### 2. Crie um ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale dependências Python

```bash
pip install -r requirements.txt
```

### 4. Configure Playwright (primeira vez)

```bash
playwright install chromium
```

---

## Executando a aplicação

### 5. Iniciar o backend FastAPI

```bash
cd backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Instale o pacote em modo editável na raiz do projeto (uma vez): `pip install -e .`

### 6. Iniciar o frontend React + Vite

```bash
cd frontend
npm install
npm run dev
```

> O frontend faz proxy das requisições para `/api` diretamente para `http://127.0.0.1:8000`.

---

## Uso

### Scan Básico

```bash
python lume_scan.py scan -u https://example.com
```

### Scan Completo com Opções

```bash
python lume_scan.py scan \
  -u https://example.com/page?id=1 \
  -o ./reports \
  -f html \
  --max-pages 50 \
  --timeout 20 \
  --verbose
```

### Opções Disponíveis

```
Options:
  -u, --url TEXT              Target URL (required)
  -o, --output PATH          Output directory (default: lume/reports)
  -f, --format [html|json|pdf]  Report format (default: html)
   --max-pages INT            Maximum crawl pages (default: 50)
   --timeout INT              Timeout seconds per phase (default: 20)

---

## Deploy no Vercel (rápido)

O repositório já inclui uma configuração mínima para deploy no Vercel.
O frontend é gerado como site estático (Vite) e a API `/api/scan` é um serverless Python
que reutiliza a lógica existente (sem alterar os módulos de scan).

Passos básicos:

```bash
# 1. Faça login no Vercel
vercel login

# 2. No diretório raiz do repositório, faça deploy (será detectado automaticamente)
vercel --prod
```

Notas:
- O builder do Vercel instalará dependências Python a partir de `requirements.txt`.
- O endpoint serverless (`api/scan.py`) executa a mesma função de análise por request.
- Scans longos podem exceder limites de execução serverless; para grandes cargas, use uma fila/worker.

  
  --no-recon                  Skip reconnaissance phase
  --no-browser                Skip browser crawling
  --no-security               Skip security testing
  --no-ssl                    Skip SSL/TLS analysis
  
  --timeout FLOAT             Request timeout (default: 10s)
  --max-pages INT             Maximum pages to crawl (default: 50)
  
  --verbose                   Enable verbose logging
```

### Exemplos Práticos

#### 1. Scan rápido (sem reconhecimento)

```bash
python lume_scan.py scan -u https://example.com --no-recon
```

#### 2. Scan profundo com relatório PDF

```bash
python lume_scan.py scan \
  -u https://example.com \
  -f pdf \
  --max-pages 100 \
  --timeout 30
```

#### 3. Apenas análise de segurança e SSL

```bash
python lume_scan.py scan \
  -u https://example.com \
  --no-recon \
  --no-browser
```

---

## Estrutura de Pastas

```
lume/
├── lume/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py              # CLI principal
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuração
│   │   └── logger.py            # Logging
│   │
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── reconnaissance.py    # Port scan, DNS, subdomínios
│   │   ├── browser.py           # Playwright crawling
│   │   ├── security.py          # Testes de vulnerabilidade
│   │   └── ssl_analysis.py      # Análise TLS/SSL
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── session.py           # Gerenciamento de conexões
│   │   ├── url_utils.py         # Utilidades de URL
│   │   └── errors.py            # Exceções customizadas
│   │
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── report_builder.py    # Construtor de relatórios
│   │   ├── formatters.py        # Exportadores (HTML/PDF/JSON)
│   │   └── templates/           # Templates Jinja2
│   │
│   ├── logs/                    # Arquivos de log
│   └── reports/                 # Relatórios gerados
│
├── lume_scan.py                 # Entry point
├── requirements.txt             # Dependências
├── README.md                    # Este arquivo
├── LICENSE                      # MIT License
└── pyproject.toml               # Configuração do projeto
```

---

## Saídas Geradas

### Relatório HTML

- Design responsivo e profissional
- Código de cores por severidade (Crítico, Alto, Médio, Baixo)
- Seções para cada tipo de finding
- Instruções práticas de remediação
- Interatividade básica

### Relatório PDF

- Versão impressa do HTML
- Ideal para compartilhamento com stakeholders
- Requer `wkhtmltopdf` instalado

### Relatório JSON

- Formato estruturado para integração
- Facilita processamento automático
- Útil para CI/CD pipelines

---

## Exemplos de Findings

### XSS Refletido
```
Tipo: XSS_REFLECTED
Parâmetro: search
Payload: "><script>alert("xss")</script>
Severidade: HIGH
Remediação: Implemente validação de entrada e encoding de saída
```

### SQL Injection
```
Tipo: SQL_INJECTION
Parâmetro: id
Payload: ' OR '1'='1'--
Severidade: CRITICAL
Remediação: Use prepared statements e queries parametrizadas
```

### Header de Segurança Ausente
```
Tipo: MISSING_SECURITY_HEADER
Header: Content-Security-Policy
Severidade: MEDIUM
Remediação: Adicione header CSP às respostas HTTP
```

---

## Princípios de Design

### SOLID

- **S**ingle Responsibility: Cada engine tem responsabilidade única
- **O**pen/Closed: Fácil adicionar novos tipos de testes
- **L**iskov Substitution: Engines intercambiáveis
- **I**nterface Segregation: Interfaces específicas
- **D**ependency Inversion: Dependência em abstrações

### RUP (Rational Unified Process)

- **Use Cases**: Cada comando CLI é um use case
- **Artifacts**: Reports bem documentados
- **Iterative**: Design preparado para evolução

---

## Tratamento de Erros

Lume é resiliente:

✓ Falha em um motor não interrompe o scan
✓ Timeout individual não bloqueia todo o processo
✓ Erros são registrados em logs detalhados
✓ Graceful degradation em dependências ausentes

Exemplo:

```
⚠ Browser crawling failed: No such file or directory: chromium
→ Lume continua com outros testes
```

---

## Performance

### Otimizações

- **Conexão Pooling**: Reutiliza conexões HTTP
- **Asyncio**: Operações paralelas
- **Multi-threading**: Escaneamento simultâneo
- **Caching**: Respostas cacheadas quando apropriado

### Benchmarks Típicos

| Operação | Tempo |
|----------|-------|
| Port Scan (5 portas) | 5-10s |
| Browser Crawl (50 páginas) | 30-60s |
| Security Tests | 10-20s |
| SSL Analysis | 3-5s |
| **Total** | **50-95s** |

---

## Limitações

- Requer Playwright browsers
- Alguns payloads podem ser bloqueados por WAF
- SSL analysis sem wkhtmltopdf usa apenas PDF em memória
- Responde somente a autorização explícita

---

## Contribuindo

Melhorias sempre bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## Roadmap

- [ ] Integração com OWASP ZAP API
- [ ] Suporte a Shodan API
- [ ] Detecção avançada de WAF
- [ ] GraphQL fuzzing
- [ ] API REST
- [ ] Dashboard Web
- [ ] Agendamento de scans
- [ ] Integração com GitLab/GitHub

---

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

---

## Disclaimer

**Lume V2.0 é fornecido "como está"**. O autor não é responsável por:

- Acesso não autorizado a sistemas
- Dados perdidos durante scans
- Impacto em produção

**Use apenas em ambientes que você possui ou tem autorização explícita.**

---

## Contato & Suporte

Para reportar issues ou sugestões:
- 📧 Email: security@example.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

*Iluminando falhas escondidas desde 2024* 🔍

---

## Passo a passo no VSCode (do zero)

1. **Criar e abrir a pasta do projeto**
   ```bash
   git clone <url-do-repositorio-lume> lume && cd lume
   ```

2. **Criar ambiente virtual e ativar**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   # ou via pyproject
   pip install .
   ```

4. **Configurar o VSCode**
   - Abra a pasta do projeto **Lume** no VSCode.
   - Selecione o interpretador Python da `.venv` (Ctrl+Shift+P → "Python: Select Interpreter").
   - Opcional: instale extensões **Python** e **Pylance**.

5. **Executar o scanner (exemplos, após `pip install -e .`)**
   ```bash
   lume scan -u https://exemplo.com --help
   lume scan -u https://exemplo.com -o ./relatorios -f html
   ```

6. **Ver relatórios**
   - Relatórios gerados na pasta indicada em `-o` (por exemplo `./relatorios` ou o padrão do comando).

7. **Rodar testes (opcional)**
   ```bash
   python -m pytest -q
   ```

---

## Como funciona (resumo técnico)

- **XSS**: injeta payloads em parâmetros de query (reais e comuns) e verifica **reflexão do payload** (incluindo encoding simples).
- **SQLi**: injeta payloads clássicos e procura **assinaturas de erro de banco** na resposta.
- **Headers**: verifica presença dos cabeçalhos recomendados (CSP, X-Frame-Options, etc.) e anota observações.

> Limitações: não faz *crawler*, não autentica, não executa *DOM-based XSS*, não faz *time-based blind SQLi*, etc. É intencionalmente simples.

---

## Exemplos de uso (prints)

Veja em `docs/prints` capturas ilustrativas da execução do CLI e do relatório Markdown.

![Execução CLI](docs/prints/run_cli.png)
![Relatório MD](docs/prints/report_md.png)

---

## Opções de linha de comando (CLI)

Use `lume scan --help` após `pip install -e .` para ver todas as opções (reconhecimento, navegador, segurança, SSL/TLS, relatórios HTML/JSON/PDF).

---

---

## Interface Web (React + TypeScript)

O projeto inclui um frontend moderno em React + TypeScript para uso via navegador:

1. **Suba a API** (em um terminal, na pasta `backend`):
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Instale e inicie o frontend** (em outro terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Acesse **http://127.0.0.1:5173** — formulário de varredura, seleção de testes e resultados.

---

## Aviso Legal

O autor **não se responsabiliza** por usos indevidos. Teste **apenas** com permissão.

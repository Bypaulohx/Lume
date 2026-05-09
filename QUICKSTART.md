# Quick Start - Lume V2.0

## 30 Segundos de Setup

### 1. Instalar

```bash
git clone https://github.com/lume-security/lume.git
cd lume
pip install -r requirements.txt
```

### 2. Instalar Playwright (primeira vez)

```bash
playwright install chromium
```

### 3. Executar Primeiro Scan

```bash
python lume_scan.py scan -u https://example.com
```

## Resultados

Seu relatório estará em: `lume/reports/lume_report_*.html`

---

## Casos de Uso Comuns

### Scan Rápido (2 minutos)

```bash
python lume_scan.py scan -u https://example.com --timeout 10 --max-pages 20
```

### Scan Profundo (5-10 minutos)

```bash
python lume_scan.py scan -u https://example.com --timeout 30 --max-pages 100
```

### Scan Sem Reconhecimento

```bash
python lume_scan.py scan -u https://example.com --no-recon
```

### Apenas Segurança

```bash
python lume_scan.py scan -u https://example.com --no-recon --no-browser --no-ssl
```

### Exportar como PDF

```bash
python lume_scan.py scan -u https://example.com -f pdf
```

---

## O que Lume Faz?

### 🔍 Reconhecimento (Reconnaissance)
- Descobre portas abertas
- Encontra subdomínios
- Coleta registros DNS

### 🌐 Análise Dinâmica (Browser)
- Renderiza JavaScript
- Encontra formulários ocultos
- Extrai endpoints

### 🛡️ Testes de Segurança (Security)
- XSS Refletido
- SQL Injection
- Headers Faltantes

### 🔐 Análise SSL/TLS
- Valida certificados
- Verifica TLS versions
- Detecta vulnerabilidades

---

## Interpretando Resultados

### Cores no Relatório

🔴 **CRÍTICO** - Corrigir imediatamente
🟠 **ALTO** - Corrigir em breve
🟡 **MÉDIO** - Considerar correção
🟢 **BAIXO** - Informacional

---

## Troubleshooting

### "Chromium not found"
```bash
playwright install chromium
```

### "nmap not found"

**Windows:**
```powershell
choco install nmap -y
```

**macOS:**
```bash
brew install nmap
```

**Linux:**
```bash
sudo apt-get install nmap
```

### Timeout
Aumentar timeout:
```bash
python lume_scan.py scan -u https://example.com --timeout 30
```

---

## Próximos Passos

1. **Ler Documentação**: Veja [README.md](README.md) para detalhes
2. **Contribuir**: Veja [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Reportar Issues**: GitHub Issues
4. **Sugerir Features**: GitHub Discussions

---

Boa sorte com seus scans! 🔒

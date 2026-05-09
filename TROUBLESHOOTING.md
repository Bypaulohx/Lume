# Troubleshooting Guide - Lume V2.0

## Problemas Comuns e Soluções

### 1. Chromium Not Found

**Erro:**
```
PlaywrightError: Chromium not found
```

**Solução:**
```bash
# Instalar Playwright browsers
playwright install chromium

# Ou instalar todos os browsers
playwright install
```

**Alternativa:**
```bash
# Desabilitar browser engine
python lume_scan.py scan -u https://example.com --no-browser
```

---

### 2. Nmap Not Found

**Erro:**
```
NmapError: nmap not found in PATH
```

**Windows:**
```powershell
# Via Chocolatey
choco install nmap -y

# Ou download em https://nmap.org/download.html
```

**macOS:**
```bash
brew install nmap
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install nmap -y
```

**Linux (RedHat/CentOS):**
```bash
sudo yum install nmap -y
```

**Solução alternativa:**
```bash
python lume_scan.py scan -u https://example.com --no-recon
```

---

### 3. PDF Generation Failed

**Erro:**
```
Error generating PDF: wkhtmltopdf not found
```

**Windows:**
```powershell
choco install wkhtmltopdf -y
```

**macOS:**
```bash
brew install --cask wkhtmltopdf
```

**Linux:**
```bash
sudo apt-get install wkhtmltopdf -y
```

**Solução alternativa:**
```bash
# Use HTML ou JSON em vez de PDF
python lume_scan.py scan -u https://example.com -f html
```

---

### 4. Connection Timeout

**Erro:**
```
ConnectionError: Connection timeout
```

**Soluções:**

1. Aumentar timeout:
```bash
python lume_scan.py scan -u https://example.com --timeout 30
```

2. Verificar conectividade:
```bash
ping example.com
```

3. Verificar firewall:
```bash
# Pode estar bloqueando a porta 443
```

4. Tentar VPN ou proxy se necessário

---

### 5. Permission Denied

**Erro (Windows):**
```
PermissionError: Access denied
```

**Solução:**
- Executar como Administrator
- Ou executar em pasta com permissões de escrita

**Erro (Linux/macOS):**
```
PermissionError: [Errno 13] Permission denied: '/usr/local/bin/nmap'
```

**Solução:**
```bash
sudo chown -R $USER /usr/local/bin
# Ou reinstalar com permissões corretas
```

---

### 6. Module Not Found

**Erro:**
```
ModuleNotFoundError: No module named 'lume'
```

**Soluções:**

1. Verificar se está no diretório correto:
```bash
cd lume  # Pasta do projeto
pwd     # Ou cd no Windows
```

2. Reinstalar dependências:
```bash
pip install -r requirements.txt
```

3. Ativar ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

---

### 7. SSL Certificate Error

**Erro:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Soluções:**

1. Verificar certificado do alvo:
```bash
openssl s_client -connect example.com:443
```

2. Desabilitar verificação TLS (com cuidado!):
```bash
# Modifique .env ou config
LUME_VERIFY_TLS=false
```

3. Instalar certificados CA:
```bash
# Windows
certifi.bat

# ou manualmente baixar certificados
```

---

### 8. Out of Memory

**Erro:**
```
MemoryError
```

**Soluções:**

1. Reduzir páginas a scanear:
```bash
python lume_scan.py scan -u https://example.com --max-pages 10
```

2. Fechar outras aplicações

3. Aumentar memória virtual (Windows)

---

### 9. WAF Detection - Blocked

**Erro:**
```
403 Forbidden / 429 Too Many Requests
```

**Soluções:**

1. Aumentar delay entre requisições:
```bash
# Modifique config.py
LUME_REQUEST_DELAY = 2  # segundos
```

2. Usar diferentes User-Agents:
```bash
# Já rotacionado automaticamente
```

3. Reduzir workers:
```bash
LUME_WORKERS=1
```

---

### 10. Database Errors

**Erro:**
```
sqlite3.OperationalError: database is locked
```

**Solução:**
```bash
# Fechar outros processos usando o banco
# Ou executar de novo após alguns segundos
```

---

## Logs de Debug

Para debug detalhado, use:

```bash
python lume_scan.py scan -u https://example.com --verbose
```

Logs serão salvos em: `lume/logs/lume_*.log`

---

## Verificação do Ambiente

Executar diagnóstico:

```python
# verify_environment.py
import platform
import sys

print(f"Python: {sys.version}")
print(f"OS: {platform.system()}")

# Verificar nmap
import subprocess
try:
    subprocess.run(["nmap", "--version"], check=True)
    print("✓ nmap instalado")
except:
    print("✗ nmap não encontrado")

# Verificar playwright
try:
    import playwright
    print("✓ playwright instalado")
except:
    print("✗ playwright não encontrado")
```

---

## Obtendo Ajuda

1. **Verificar logs**: `lume/logs/` para detalhes
2. **GitHub Issues**: Report com logs e ambiente
3. **Stack Overflow**: Tag `[lume-security]`
4. **Email**: security@lume.local

---

## Performance Tips

1. **Usar --no-recon** se não precisar de port scan
2. **Reduzir --max-pages** para alvos grandes
3. **Aumentar LUME_WORKERS** para máquinas poderosas
4. **Usar --timeout maior** para conexões lentas

---

Precisa de mais ajuda? Veja [README.md](README.md) ou abra uma issue no GitHub.

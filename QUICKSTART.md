# Quick Start - Lume V2.0

## ⚡ Setup Rápido (5 minutos)

### 1. Clonar e Preparar

```bash
git clone https://github.com/lume-security/lume.git
cd lume
```

### 2. Criar Virtual Environment (Windows)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Alternativa (Linux/macOS):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Instalar Playwright Browsers

```bash
python -m playwright install chromium
```

---

## 🚀 Executar Localmente

### Opção A: Interface Web (Backend + Frontend)

#### Terminal 1 - Backend FastAPI

Na raiz do repositório (com `.venv` ativado):

```powershell
# Windows / Linux / macOS — sempre a partir da pasta backend
cd backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Você verá:
```
Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2 - Frontend React + Vite

```powershell
cd frontend
npm install
npm run dev
```

Você verá algo como:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://127.0.0.1:5173/
```

#### Abrir no Navegador

Acesse: **http://127.0.0.1:5173** (recomendado; evita ambiguidades de `localhost` no Windows).

Digite a URL alvo e clique em **Iniciar varredura**.

---

### Opção B: CLI (Linha de Comando)

```bash
# Scan Rápido (2 minutos)
python lume_scan.py scan -u https://example.com --timeout 10 --max-pages 20
```

```bash
# Scan Profundo (5-10 minutos)
python lume_scan.py scan -u https://example.com --timeout 30 --max-pages 100
```

```bash
# Apenas Headers e Segurança
python lume_scan.py scan -u https://example.com --no-recon --no-browser --no-ssl
```

---

## 📊 Resultados

- **Web UI**: Resultados em tempo real no navegador
- **CLI**: Relatório em `lume/reports/lume_report_*.html`

Abra o relatório HTML em qualquer navegador.

---

## ✅ Verificar Instalação

```bash
python -m playwright --version
python -m uvicorn --version
python -c "import fastapi; print(fastapi.__version__)"
python -m py_compile backend/api/main.py
```

---

## 🔧 Troubleshooting

### "playwright not found"
```bash
python -m playwright install chromium
```

### "uvicorn not found"
Certifique-se que o `.venv` está ativado e execute `pip install -r requirements.txt`.

### Porta 8000 já em uso
```bash
cd backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001
```

Ajuste também o `target` do proxy em `frontend/vite.config.ts` para `http://127.0.0.1:8001`.

---

## 🎯 Próximos Passos

1. **Testar no navegador**: http://127.0.0.1:5173
2. **Escanear um site**: Digite a URL e inicie a varredura
3. **Documentação completa**: [README.md](README.md)

---

Pronto para começar.

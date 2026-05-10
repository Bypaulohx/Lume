# Lume — Frontend

Interface React + TypeScript para análise de segurança web (Lume V2.0).

## Como rodar

1. **Instale as dependências:**
   ```bash
   npm install
   ```

2. **Suba a API** (outro terminal, pasta `backend` na raiz do repositório):
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
   ```

   Na raiz do projeto, execute uma vez: `pip install -e .` para instalar o pacote `lume`.

3. **Inicie o frontend:**
   ```bash
   npm run dev
   ```

4. Acesse: **http://127.0.0.1:5173**

O Vite faz proxy de `/api` para `http://127.0.0.1:8000`.

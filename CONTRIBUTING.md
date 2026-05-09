# Contributing to Lume

Obrigado por considerar contribuir para Lume V2.0!

## Como Contribuir

### 1. Reportar Bugs

Quando encontrar um bug, abra uma Issue com:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Versão do Python e SO
- Logs relevantes

### 2. Sugerir Melhorias

Tem uma ideia? Abra uma Issue com:

- Descrição clara da melhoria
- Casos de uso
- Possíveis implementações
- Exemplos de código (se aplicável)

### 3. Pull Requests

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/sua-feature`
3. Faça commits descritivos
4. Push para sua branch
5. Abra um Pull Request

### Diretrizes de Código

- Seguir PEP 8
- Adicionar docstrings em funções públicas
- Testes para novas features
- Atualizar README se necessário

### Setup de Desenvolvimento

```bash
git clone https://github.com/seu-usuario/lume.git
cd lume

python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

pip install -r requirements.txt
pip install black flake8 pytest

# Setup pre-commit hooks
pre-commit install
```

### Executar Testes

```bash
pytest tests/ -v
```

### Formato de Código

```bash
# Format
black lume/ --line-length=100

# Lint
flake8 lume/ --max-line-length=100
```

## Processo de Review

1. Verificamos se o código segue os padrões
2. Executamos testes automatizados
3. Testamos manualmente se aplicável
4. Fornecemos feedback

## Código de Conduta

- Seja respeitoso
- Aceite críticas construtivas
- Reporte problemas apropriadamente

## Obrigado!

Sua contribuição é muito valiosa para Lume.

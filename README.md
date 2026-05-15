# Bug Hunter — Backend

Suite de testes automatizados aplicada a uma API REST em **FastAPI**. Demonstra testes funcionais, de contrato, de validação e de regressão usando **pytest** e **requests/httpx**. CI configurado com GitHub Actions e relatório de cobertura.

---

## Stack

- **Python 3.11+**
- **FastAPI** — framework da API sob teste
- **pytest** — runner de testes
- **httpx** — cliente HTTP assíncrono (TestClient)
- **pytest-cov** — relatório de cobertura
- **GitHub Actions** — CI/CD

---

## Estrutura

```
bughunter-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # endpoints da API
│   ├── models.py         # schemas Pydantic
│   ├── validators.py     # validações reutilizáveis
│   └── storage.py        # camada de dados em memória
├── tests/
│   ├── conftest.py       # fixtures compartilhadas
│   ├── test_auth.py      # cadastro e login
│   ├── test_tasks.py     # CRUD de tarefas
│   └── test_validators.py # validators isolados
├── requirements.txt
├── pytest.ini
└── .github/workflows/
    └── ci.yml
```

---

## Como rodar

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

```bash
pip install -r requirements.txt
```

### Rodar a API localmente

```bash
uvicorn app.main:app --reload
```

Documentação interativa em `http://localhost:8000/docs`.

### Rodar os testes

```bash
pytest                           # todos os testes
pytest -v                        # modo verboso
pytest --cov=app --cov-report=term-missing  # cobertura
pytest tests/test_auth.py        # arquivo específico
pytest -k "login"                # filtra por nome
```

---

## O que está sendo testado

### Testes funcionais
- Cadastro com dados válidos e inválidos (formato de email, senha curta, duplicidade)
- Login com credenciais corretas, incorretas e variações de caixa (regressão BUG-002)
- CRUD completo de tarefas

### Testes de validação
- Casos de borda em todos os campos (vazios, máximos, caracteres especiais)
- Tipos inválidos
- Tamanho de payload

### Testes de contrato
- Estrutura de resposta para cada endpoint
- Códigos HTTP esperados (200, 201, 400, 401, 404, 422)
- Cabeçalhos e tipos MIME

### Testes de regressão
- Bugs do projeto de teste manual reproduzidos e travados como testes automatizados

---

## Pipeline de CI

A cada push ou PR para `main`, o GitHub Actions executa:

1. Lint com `ruff`
2. Testes com `pytest` e cobertura
3. Upload do relatório HTML como artifact

[![CI](https://github.com/SEU_USUARIO/bughunter-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/SEU_USUARIO/bughunter-backend/actions)

---

## Cobertura atual

| Métrica | Valor |
|---|---|
| Statements | ~95% |
| Branches | ~90% |
| Lines | ~95% |

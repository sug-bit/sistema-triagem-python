# 🏥 Sistema de Triagem Hospitalar

Projeto HealthTech criado por **Gustavo Victorino**, técnico de enfermagem na SPDM e estudante de ADS no Centro Universitário Piaget (2026-2028). Ele une a vivência hospitalar com programação: cadastra pacientes, classifica o risco pelo **Protocolo de Manchester** e organiza a fila de atendimento por prioridade.


## Funcionalidades
- Cadastro e login de usuários, com validação de todos os campos
- Cadastro de pacientes (nome, idade, queixa principal e classificação de risco)
- Fila ordenada por prioridade e, dentro da mesma cor, por ordem de chegada
- Botões **Chamar próximo** e **Remover**, contadores por cor e último paciente chamado
- Layout responsivo, com modo escuro e navegação por teclado

## Classificação de risco (Manchester)
| Cor | Gravidade | Meta de atendimento |
|---|---|---|
| 🔴 Vermelho | Emergência | Imediato |
| 🟠 Laranja | Muito urgente | até 10 min |
| 🟡 Amarelo | Urgente | até 60 min |
| 🟢 Verde | Pouco urgente | até 120 min |
| 🔵 Azul | Não urgente | até 240 min |

## Três versões no mesmo repositório
| Versão | Pasta | Tecnologias | Onde os dados ficam |
|---|---|---|---|
| Web estática | `index.html` (raiz) | HTML5, CSS3, JavaScript | No navegador (`localStorage`) |
| Web com servidor | `backend/` | Python 3, Flask, SQLite, HTML, CSS, JavaScript | Banco SQLite no servidor |
| Terminal | `cli/` | Python 3 | Em memória |

**Linguagens e recursos usados:** Python (lógica, Flask, SQLite), JavaScript (interface, validações, chamadas à API com `fetch`, Web Crypto API), HTML5 e CSS3 (layout responsivo com Grid/Flexbox e variáveis CSS).

## Como rodar

**1. Versão estática (a mais simples)**
Abra o `index.html` no navegador. Para publicar, ative o **GitHub Pages** nas configurações do repositório (branch `main`, pasta raiz).

**2. Versão com backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Acesse http://127.0.0.1:5000. Em produção, defina a variável `SECRET_KEY` com um valor longo e aleatório.

**3. Versão terminal**
```bash
python cli/main.py
```

## Como funciona o login
- **Estática:** a conta fica no `localStorage`. A senha é guardada com **hash SHA-256 e salt**, gerados pela Web Crypto API. É uma demonstração: quem tem acesso ao navegador consegue ver os dados.
- **Backend:** a senha é guardada com hash e salt (Werkzeug), a sessão usa cookie `HttpOnly` e todas as regras são validadas de novo no servidor. Cada usuário só acessa os próprios pacientes.

## API (versão com backend)
| Método | Rota | Função |
|---|---|---|
| POST | `/api/register` | Criar conta |
| POST | `/api/login` | Entrar |
| POST | `/api/logout` | Sair |
| GET | `/api/me` | Dados do usuário logado |
| GET | `/api/fila` | Fila ordenada |
| POST | `/api/pacientes` | Adicionar paciente |
| DELETE | `/api/pacientes/<id>` | Remover paciente |
| POST | `/api/chamar` | Chamar o próximo da fila |

## Estrutura
```
├── index.html            # versão estática (GitHub Pages)
├── backend/
│   ├── app.py            # API Flask + SQLite
│   ├── requirements.txt
│   └── static/index.html # front-end que conversa com a API
├── cli/main.py           # versão original em terminal
└── README.md
```

## Próximos passos
Limite de tentativas de login, recuperação de senha, histórico de atendimentos, alerta visual para paciente que passou da meta de espera e testes automatizados.

## Autor
**Gustavo Victorino** – Técnico de Enfermagem | Estudante de ADS no Centro Universitário Piaget
[LinkedIn](https://www.linkedin.com/in/gustavo-victorino-06405b239/)

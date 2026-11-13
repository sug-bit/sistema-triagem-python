"""API Flask da Triagem Hospitalar: login com sessão, SQLite e fila por prioridade."""
import os, re, sqlite3, time
from functools import wraps
from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "triagem.db")
PRIORIDADES = ["VERMELHO", "LARANJA", "AMARELO", "VERDE", "AZUL"]  # Manchester
EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def fechar(_):
    conexao = g.pop("db", None)
    if conexao:
        conexao.close()


def init():
    with sqlite3.connect(DB) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios(
          id INTEGER PRIMARY KEY, nome TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL, senha_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pacientes(
          id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
          nome TEXT NOT NULL, idade INTEGER NOT NULL, queixa TEXT NOT NULL,
          prioridade TEXT NOT NULL, chegada INTEGER NOT NULL, chamado INTEGER NOT NULL DEFAULT 0);""")


def erro(msg, codigo=400):
    return jsonify(erro=msg), codigo


def login_required(f):
    @wraps(f)
    def interno(*a, **k):
        if "uid" not in session:
            return erro("Faça login para continuar.", 401)
        return f(*a, **k)
    return interno


def dados(uid):
    linhas = db().execute("SELECT * FROM pacientes WHERE usuario_id=? ORDER BY id", (uid,)).fetchall()
    fila = [dict(r) for r in linhas if not r["chamado"]]
    fila.sort(key=lambda p: (PRIORIDADES.index(p["prioridade"]), p["chegada"]))
    chamados = [{"nome": r["nome"], "prioridade": r["prioridade"]} for r in linhas if r["chamado"]]
    return {"fila": fila, "chamados": chamados}


def perfil(u):
    return {"email": u["email"], "nome": u["nome"], "dados": dados(u["id"])}


@app.get("/")
def home():
    return app.send_static_file("index.html")


@app.post("/api/register")
def register():
    j = request.get_json(silent=True) or {}
    nome, email, senha = (j.get("nome") or "").strip(), (j.get("email") or "").strip().lower(), j.get("senha") or ""
    if len(nome.split()) < 2:
        return erro("Informe nome e sobrenome.")
    if not EMAIL.match(email):
        return erro("Digite um e-mail válido.")
    if len(senha) < 8 or not re.search(r"[A-Za-z]", senha) or not re.search(r"\d", senha):
        return erro("A senha precisa de 8 caracteres ou mais, com letras e números.")
    if db().execute("SELECT 1 FROM usuarios WHERE email=?", (email,)).fetchone():
        return erro("Já existe uma conta com esse e-mail. Entre ou use outro e-mail.", 409)
    cur = db().execute("INSERT INTO usuarios(nome,email,senha_hash) VALUES(?,?,?)",
                       (nome, email, generate_password_hash(senha)))
    db().commit()
    session.clear()
    session["uid"] = cur.lastrowid
    return jsonify(perfil(db().execute("SELECT * FROM usuarios WHERE id=?", (cur.lastrowid,)).fetchone()))


@app.post("/api/login")
def login():
    j = request.get_json(silent=True) or {}
    u = db().execute("SELECT * FROM usuarios WHERE email=?", ((j.get("email") or "").strip().lower(),)).fetchone()
    if not u or not check_password_hash(u["senha_hash"], j.get("senha") or ""):
        return erro("E-mail ou senha incorretos.", 401)
    session.clear()
    session["uid"] = u["id"]
    return jsonify(perfil(u))


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/me")
@login_required
def me():
    return jsonify(perfil(db().execute("SELECT * FROM usuarios WHERE id=?", (session["uid"],)).fetchone()))


@app.get("/api/fila")
@login_required
def fila():
    return jsonify(dados(session["uid"]))


@app.post("/api/pacientes")
@login_required
def novo_paciente():
    j = request.get_json(silent=True) or {}
    nome, queixa, prio = (j.get("nome") or "").strip(), (j.get("queixa") or "").strip(), j.get("prioridade")
    idade = j.get("idade")
    if len(nome) < 3 or len(queixa) < 3 or len(queixa) > 80:
        return erro("Informe nome (mínimo 3 letras) e queixa principal (3 a 80 caracteres).")
    if not isinstance(idade, int) or isinstance(idade, bool) or not 0 <= idade <= 120:
        return erro("Informe uma idade entre 0 e 120.")
    if prio not in PRIORIDADES:
        return erro("Escolha uma classificação de risco válida.")
    db().execute("INSERT INTO pacientes(usuario_id,nome,idade,queixa,prioridade,chegada) VALUES(?,?,?,?,?,?)",
                 (session["uid"], nome, idade, queixa, prio, int(time.time() * 1000)))
    db().commit()
    return jsonify(dados(session["uid"])), 201


@app.delete("/api/pacientes/<int:pid>")
@login_required
def remover(pid):
    db().execute("DELETE FROM pacientes WHERE id=? AND usuario_id=?", (pid, session["uid"]))
    db().commit()
    return jsonify(dados(session["uid"]))


@app.post("/api/chamar")
@login_required
def chamar():
    fila_atual = dados(session["uid"])["fila"]
    if fila_atual:
        db().execute("UPDATE pacientes SET chamado=1 WHERE id=? AND usuario_id=?", (fila_atual[0]["id"], session["uid"]))
        db().commit()
    return jsonify(dados(session["uid"]))


init()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")

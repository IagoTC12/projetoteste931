"""
EcoHábitos — Avaliação Ambiental Pessoal

Como rodar:
    pip install -r requirements.txt
    python main.py
Depois abra http://127.0.0.1:5000 no navegador.

O banco de dados (arquivo ecohabitos.db) é criado sozinho na primeira execução.
"""

import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# A SECRET_KEY protege a sessão (o "estar logado"). Em produção, defina a
# variável de ambiente SECRET_KEY com um valor longo e aleatório.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
app.config["DATABASE"] = os.path.join(app.root_path, "ecohabitos.db")


# ---------------------------------------------------------------------------
# Regras de pontuação
# ---------------------------------------------------------------------------
# "sugestao" aparece para o usuário quando ele registra uma ação prejudicial.
REGRAS = {
    "bicicleta": {
        "nome": "Ir de bicicleta",
        "pontos": 10,
        "categoria": "Positiva",
    },
    "transporte": {
        "nome": "Usar transporte público",
        "pontos": 6,
        "categoria": "Positiva",
    },
    "reciclagem": {
        "nome": "Separar resíduos recicláveis",
        "pontos": 5,
        "categoria": "Positiva",
    },
    "neutra": {
        "nome": "Realizar uma atividade neutra",
        "pontos": 0,
        "categoria": "Neutra",
    },
    "plastico": {
        "nome": "Usar plástico descartável",
        "pontos": -3,
        "categoria": "Prejudicial",
        "sugestao": "Leve uma garrafa, copo ou sacola reutilizável. "
                    "Pequenas trocas evitam muito lixo plástico.",
    },
    "banho_longo": {
        "nome": "Tomar banho longo (mais de 15 min)",
        "pontos": -3,
        "categoria": "Prejudicial",
        "sugestao": "Tente banhos de até 5 a 10 minutos e feche o chuveiro "
                    "enquanto se ensaboa.",
    },
    "carro": {
        "nome": "Fazer um trajeto de carro",
        "pontos": -5,
        "categoria": "Prejudicial",
        "sugestao": "Para trajetos curtos, experimente ir a pé ou de bicicleta. "
                    "Para trajetos longos, considere transporte público ou carona.",
    },
}


# ---------------------------------------------------------------------------
# Banco de dados (SQLite — já vem com o Python, não precisa instalar nada)
# ---------------------------------------------------------------------------
def get_db():
    """Abre uma conexão com o banco (uma por requisição)."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def fechar_db(_erro=None):
    """Fecha a conexão ao fim de cada requisição."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def criar_tabelas():
    """Cria as tabelas se ainda não existirem."""
    with app.app_context():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT NOT NULL UNIQUE COLLATE NOCASE,
                senha_hash  TEXT NOT NULL,
                criado_em   TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS atividades (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id  INTEGER NOT NULL
                            REFERENCES usuarios(id) ON DELETE CASCADE,
                tipo        TEXT NOT NULL,
                nome        TEXT NOT NULL,
                categoria   TEXT NOT NULL,
                pontos      INTEGER NOT NULL,
                quantidade  TEXT NOT NULL,
                criado_em   TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE INDEX IF NOT EXISTS idx_atividades_usuario
                ON atividades(usuario_id);
            """
        )
        db.commit()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@app.before_request
def carregar_usuario():
    """Antes de cada página, descobre quem está logado (ou ninguém)."""
    g.usuario = None
    usuario_id = session.get("usuario_id")
    if usuario_id is not None:
        g.usuario = get_db().execute(
            "SELECT id, nome FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        if g.usuario is None:  # usuário foi apagado do banco
            session.clear()


def login_obrigatorio(funcao):
    """Coloque @login_obrigatorio em rotas que exigem estar logado."""
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if g.usuario is None:
            flash("Entre na sua conta para continuar.", "aviso")
            return redirect(url_for("login"))
        return funcao(*args, **kwargs)
    return protegida


@app.template_filter("data_br")
def data_br(texto):
    """Mostra '2026-10-27 19:47:00' como '27/10/2026 19:47'."""
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return texto


# ---------------------------------------------------------------------------
# Rotas: conta
# ---------------------------------------------------------------------------
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if g.usuario:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar", "")

        erro = None
        if not 3 <= len(nome) <= 30:
            erro = "O nome de usuário deve ter entre 3 e 30 caracteres."
        elif len(senha) < 6:
            erro = "A senha deve ter pelo menos 6 caracteres."
        elif senha != confirmar:
            erro = "As senhas não são iguais."

        if erro is None:
            db = get_db()
            try:
                cursor = db.execute(
                    "INSERT INTO usuarios (nome, senha_hash) VALUES (?, ?)",
                    (nome, generate_password_hash(senha)),
                )
                db.commit()
            except sqlite3.IntegrityError:
                erro = "Esse nome de usuário já está em uso."
            else:
                session.clear()
                session["usuario_id"] = cursor.lastrowid
                flash(f"Bem-vindo(a), {nome}! Registre sua primeira atividade.", "sucesso")
                return redirect(url_for("inicio"))

        flash(erro, "erro")

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")

        usuario = get_db().execute(
            "SELECT id, nome, senha_hash FROM usuarios WHERE nome = ?", (nome,)
        ).fetchone()

        # Mesma mensagem nos dois casos, para não revelar quais usuários existem
        if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
            flash("Usuário ou senha incorretos.", "erro")
        else:
            session.clear()
            session["usuario_id"] = usuario["id"]
            return redirect(url_for("inicio"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Rotas: atividades
# ---------------------------------------------------------------------------
@app.route("/")
@login_obrigatorio
def inicio():
    db = get_db()
    atividades = db.execute(
        "SELECT * FROM atividades WHERE usuario_id = ? ORDER BY id DESC",
        (g.usuario["id"],),
    ).fetchall()

    pontuacao = sum(a["pontos"] for a in atividades)

    # Uma sugestão para cada tipo de ação prejudicial que o usuário registrou
    sugestoes = []
    vistos = set()
    for a in atividades:
        regra = REGRAS.get(a["tipo"])
        if a["pontos"] < 0 and a["tipo"] not in vistos and regra and regra.get("sugestao"):
            vistos.add(a["tipo"])
            sugestoes.append({"nome": regra["nome"], "texto": regra["sugestao"]})

    return render_template(
        "index.html",
        pontuacao=pontuacao,
        atividades=atividades,
        regras=REGRAS,
        sugestoes=sugestoes,
    )


@app.route("/registrar", methods=["POST"])
@login_obrigatorio
def registrar():
    tipo = request.form.get("tipo", "")
    quantidade = request.form.get("quantidade", "").strip()

    if tipo not in REGRAS:
        flash("Atividade inválida.", "erro")
        return redirect(url_for("inicio"))

    if not quantidade or len(quantidade) > 100:
        flash("Informe uma quantidade ou descrição (até 100 caracteres).", "erro")
        return redirect(url_for("inicio"))

    regra = REGRAS[tipo]
    db = get_db()
    # Guardamos nome/categoria/pontos do momento do registro: se as regras
    # mudarem no futuro, o histórico antigo continua igual.
    db.execute(
        """INSERT INTO atividades
               (usuario_id, tipo, nome, categoria, pontos, quantidade)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (g.usuario["id"], tipo, regra["nome"], regra["categoria"],
         regra["pontos"], quantidade),
    )
    db.commit()

    flash(f"Atividade registrada: {regra['nome']} ({regra['pontos']:+d} pontos).", "sucesso")
    return redirect(url_for("inicio"))


@app.route("/excluir/<int:atividade_id>", methods=["POST"])
@login_obrigatorio
def excluir(atividade_id):
    db = get_db()
    # O "AND usuario_id = ?" impede que alguém apague atividade de outra pessoa
    resultado = db.execute(
        "DELETE FROM atividades WHERE id = ? AND usuario_id = ?",
        (atividade_id, g.usuario["id"]),
    )
    db.commit()

    if resultado.rowcount:
        flash("Atividade removida.", "sucesso")
    else:
        flash("Atividade não encontrada.", "erro")
    return redirect(url_for("inicio"))


@app.route("/ranking")
@login_obrigatorio
def ranking():
    usuarios = get_db().execute(
        """SELECT u.id, u.nome,
                  COALESCE(SUM(a.pontos), 0) AS pontuacao,
                  COUNT(a.id)                AS total
             FROM usuarios u
             LEFT JOIN atividades a ON a.usuario_id = u.id
            GROUP BY u.id
            ORDER BY pontuacao DESC, u.nome"""
    ).fetchall()
    return render_template("ranking.html", usuarios=usuarios)


# Cria as tabelas ao iniciar (funciona tanto com "python main.py" quanto "flask run")
criar_tabelas()

if __name__ == "__main__":
    app.run(debug=True)

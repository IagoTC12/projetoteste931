
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Regras iniciais de pontuacao
REGRAS = {
    "bicicleta": {
        "nome": "Ir de bicicleta",
        "pontos": 10,
        "categoria": "Positiva"
    },
    "reciclagem": {
        "nome": "Separar resíduos recicláveis",
        "pontos": 5,
        "categoria": "Positiva"
    },
    "transporte": {
        "nome": "Usar transporte público",
        "pontos": 6,
        "categoria": "Positiva"
    },
    "neutra": {
        "nome": "Realizar uma atividade neutra",
        "pontos": 0,
        "categoria": "Neutra"
    },
    "carro": {
        "nome": "Fazer um trajeto de carro",
        "pontos": -5,
        "categoria": "Prejudicial"
    }
}

# Temporario: os registros ficam na memoria
atividades = []


@app.route("/")
def inicio():
    pontuacao = sum(
        atividade["pontos"] for atividade in atividades
    )

    return render_template(
        "index.html",
        regras=REGRAS,
        atividades=atividades,
        pontuacao=pontuacao
    )


@app.route("/registrar", methods=["POST"])
def registrar():
    tipo = request.form.get("tipo", "")
    quantidade = request.form.get("quantidade", "").strip()

    # Validacao basica dos dados recebidos
    if tipo not in REGRAS:
        return "Atividade inválida.", 400

    if not quantidade or len(quantidade) > 100:
        return "Informe uma quantidade ou descricao valida.", 400

    regra = REGRAS[tipo]

    atividades.append({
        "nome": regra["nome"],
        "categoria": regra["categoria"],
        "quantidade": quantidade,
        "pontos": regra["pontos"]
    })

    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)

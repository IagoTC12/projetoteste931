# 🌱 EcoHábitos — Avaliação Ambiental Pessoal

Site para registrar hábitos do dia a dia e ver como eles afetam o meio ambiente. Cada atividade vale pontos, o site sugere como melhorar os hábitos prejudiciais e um ranking compara os participantes.

> *Pequenas atitudes, grandes mudanças.*

## 📋 Sobre o projeto

- 🌍 **Objetivo:** conscientizar as pessoas sobre como seus hábitos cotidianos afetam o meio ambiente e contribuem para as mudanças climáticas.
- ✍️ **Registro manual:** cada usuário registra as atividades que fez, com uma quantidade ou descrição (ex.: "5 km", "3 garrafas").
- 💡 **Sugestões de melhoria:** quando o usuário registra uma ação prejudicial, aparece uma dica de como trocar esse hábito.
- 🏆 **Ranking:** os participantes comparam sua pontuação com a dos demais.
- 🔐 **Contas de usuário:** cada pessoa tem login e senha, e vê e edita só o próprio histórico.

## 📊 Sistema de pontuação

| Atividade | Categoria | Pontos |
|---|---|---|
| Ir de bicicleta | 🟢 Positiva | +10 |
| Usar transporte público | 🟢 Positiva | +6 |
| Separar resíduos recicláveis | 🟢 Positiva | +5 |
| Realizar uma atividade neutra | ⚪ Neutra | 0 |
| Usar plástico descartável | 🔴 Prejudicial | −3 |
| Tomar banho longo (mais de 15 min) | 🔴 Prejudicial | −3 |
| Fazer um trajeto de carro | 🔴 Prejudicial | −5 |

- 🟢 **Ações positivas** aumentam a pontuação.
- ⚪ **Ações neutras** não alteram a pontuação.
- 🔴 **Ações prejudiciais** diminuem a pontuação e mostram uma sugestão de melhoria.

A pontuação do usuário é a soma dos pontos de todas as atividades registradas. Ao remover uma atividade, o total é recalculado.

## 🚀 Como rodar

**Requisito:** [Python](https://www.python.org/downloads/) 3.9 ou mais novo.

1. Abra o terminal **dentro da pasta do projeto** (a que tem o `main.py`):

   ```bash
   cd caminho/para/ecohabitos
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicie o servidor:

   ```bash
   python main.py
   ```

4. Abra **http://127.0.0.1:5000** no navegador.

Para parar o servidor, aperte `Ctrl + C` no terminal.

> ⚠️ Se aparecer `Could not open requirements file`, o terminal não está na pasta do projeto. Volte ao passo 1.

## 🧭 Como usar

1. Clique em **Criar conta** e escolha um nome de usuário (3 a 30 caracteres) e uma senha (mínimo 6 caracteres).
2. Em **Registrar atividade**, escolha o que você fez e informe a quantidade ou uma descrição.
3. Acompanhe sua pontuação, o histórico e as sugestões na página **Minhas atividades**.
4. Veja sua posição em relação aos outros participantes na página **Ranking**.

## 🗄️ Banco de dados

O projeto usa o **SQLite**, que já vem com o Python, então não é preciso instalar nenhum banco.

- Na primeira execução é criado automaticamente o arquivo `ecohabitos.db` na pasta do projeto.
- Ele guarda duas tabelas: `usuarios` (nome e senha criptografada) e `atividades` (o que cada usuário registrou).
- Os dados continuam salvos quando o servidor é desligado.
- Para **zerar tudo**, pare o servidor e apague o arquivo `ecohabitos.db`. Um novo arquivo vazio é criado na próxima execução.

Para ver o conteúdo do banco, use o [DB Browser for SQLite](https://sqlitebrowser.org/), que é gratuito.

## 📁 Estrutura do projeto

```
ecohabitos/
├── main.py              # Aplicação Flask: rotas, regras de pontuação e banco de dados
├── requirements.txt     # Dependências (Flask)
├── readme.md            # Este arquivo
├── ecohabitos.db        # Banco de dados (criado ao rodar pela primeira vez)
└── templates/           # Páginas HTML (Jinja2)
    ├── base.html        # Layout comum: cabeçalho, menu, mensagens e estilos
    ├── cadastro.html    # Criar conta
    ├── login.html       # Entrar
    ├── index.html       # Pontuação, registro, sugestões e histórico
    └── ranking.html     # Ranking de participantes
```

## ✏️ Como adicionar ou mudar atividades

As atividades ficam no dicionário `REGRAS`, no `main.py`. Para criar uma atividade nova, acrescente uma entrada nesse formato:

```python
"compostagem": {
    "nome": "Fazer compostagem",
    "pontos": 4,
    "categoria": "Positiva",   # Positiva, Neutra ou Prejudicial
},
```

Nas atividades prejudiciais, inclua também a chave `"sugestao"` com a dica que deve aparecer para o usuário.

Mudar os pontos de uma atividade não altera o que já foi registrado. O histórico guarda os pontos que valiam no momento do registro.

## 🛠️ Tecnologias

- [Python](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/)
- [SQLite](https://www.sqlite.org/) (banco de dados)
- HTML e CSS com templates [Jinja2](https://jinja.palletsprojects.com/)

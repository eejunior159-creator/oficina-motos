from flask import Flask, render_template_string, request, redirect
from datetime import datetime
import os
import psycopg2

app = Flask(__name__)

# ================= BANCO =================
DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

def criar_tabela():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS motos (
            id SERIAL PRIMARY KEY,
            placa TEXT NOT NULL,
            modelo TEXT NOT NULL,
            mecanico TEXT NOT NULL,
            servico TEXT NOT NULL,
            status TEXT NOT NULL,
            entrada TEXT NOT NULL,
            saida TEXT
        )
    """)
    con.commit()
    con.close()

criar_tabela()

# ================= ROTAS =================
@app.route("/", methods=["GET", "POST"])
def index():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        placa = request.form["placa"]
        modelo = request.form["modelo"]
        mecanico = request.form["mecanico"]
        servico = request.form["servico"]
        entrada = datetime.now().strftime("%d/%m/%Y %H:%M")

        cur.execute("""
            INSERT INTO motos (placa, modelo, mecanico, servico, status, entrada)
            VALUES (%s, %s, %s, %s, 'Em andamento', %s)
        """, (placa, modelo, mecanico, servico, entrada))
        con.commit()
        return redirect("/")

    cur.execute("SELECT * FROM motos WHERE saida IS NULL ORDER BY entrada")
    motos = cur.fetchall()
    con.close()

    return render_template_string(TEMPLATE, motos=motos)

@app.route("/saida/<int:id>")
def saida(id):
    con = conectar()
    cur = con.cursor()
    saida = datetime.now().strftime("%d/%m/%Y %H:%M")
    cur.execute("""
        UPDATE motos
        SET saida=%s, status='Finalizado'
        WHERE id=%s
    """, (saida, id))
    con.commit()
    con.close()
    return redirect("/")

# ================= HTML =================
TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Oficina de Motos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-4">
    <h2 class="mb-4">🏍️ Controle da Oficina</h2>

    <div class="card mb-4 shadow-sm">
        <div class="card-body">
            <form method="post" class="row g-2">
                <div class="col-md-2">
                    <input name="placa" class="form-control" placeholder="Placa" required>
                </div>
                <div class="col-md-3">
                    <input name="modelo" class="form-control" placeholder="Modelo" required>
                </div>
                <div class="col-md-3">
                    <input name="mecanico" class="form-control" placeholder="Mecânico" required>
                </div>
                <div class="col-md-3">
                    <input name="servico" class="form-control" placeholder="Serviço" required>
                </div>
                <div class="col-md-1 d-grid">
                    <button class="btn btn-success">Entrada</button>
                </div>
            </form>
        </div>
    </div>

    <div class="card shadow-sm">
        <div class="card-body">
            <table class="table table-striped align-middle">
                <thead>
                    <tr>
                        <th>Placa</th>
                        <th>Modelo</th>
                        <th>Mecânico</th>
                        <th>Serviço</th>
                        <th>Status</th>
                        <th>Entrada</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody>
                {% for m in motos %}
                    <tr>
                        <td>{{m[1]}}</td>
                        <td>{{m[2]}}</td>
                        <td>{{m[3]}}</td>
                        <td>{{m[4]}}</td>
                        <td><span class="badge bg-warning">{{m[5]}}</span></td>
                        <td>{{m[6]}}</td>
                        <td>
                            <a href="/saida/{{m[0]}}" class="btn btn-danger btn-sm">Saída</a>
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)

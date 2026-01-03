import os
import psycopg2
from flask import Flask, render_template, request, redirect
from datetime import date

app = Flask(__name__)

# ===============================
# CONEXÃO COM BANCO (RENDER)
# ===============================
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# ===============================
# CRIA TABELA SE NÃO EXISTIR
# ===============================
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS motos (
            id SERIAL PRIMARY KEY,
            placa TEXT,
            modelo TEXT,
            mecanico TEXT,
            servico TEXT,
            hora_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hora_saida TIMESTAMP,
            status TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()


# ===============================
# ROTAS
# ===============================

# Página principal – motos em serviço
@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute("""
            INSERT INTO motos (placa, modelo, mecanico, servico, status)
            VALUES (%s, %s, %s, %s, 'aberto')
        """, (
            request.form["placa"],
            request.form["modelo"],
            request.form["mecanico"],
            request.form["servico"]
        ))
        conn.commit()

    cur.execute("""
    SELECT *
    FROM motos
    WHERE saida IS NULL
    ORDER BY entrada DESC
""")

    motos = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("index.html", motos=motos)


# Finalizar serviço (dar saída)
@app.route("/saida/<int:id>")
def saida(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE motos
        SET status = 'finalizado', hora_saida = NOW()
        WHERE id = %s
    """, (id,))

    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")


# Histórico de motos finalizadas HOJE
@app.route("/historico-hoje")
def historico_hoje():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM motos
        WHERE status = 'finalizado'
        AND DATE(hora_saida) = CURRENT_DATE
        ORDER BY hora_saida
    """)
    motos = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("historico_hoje.html", motos=motos)


# Página de impressão do dia
@app.route("/imprimir")
def imprimir():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM motos
        WHERE DATE(hora_saida) = CURRENT_DATE
        ORDER BY hora_saida
    """)
    motos = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("imprimir.html", motos=motos)


# ===============================
# RODAR LOCAL (opcional)
# ===============================
if __name__ == "__main__":
    app.run(debug=True)

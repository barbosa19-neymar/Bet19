import streamlit as st
import random
import sqlite3
from datetime import datetime

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

st.set_page_config(
    page_title="Bet da Sorte - Demo",
    page_icon="🎰",
    layout="wide"
)

DB = "bet_demo.db"

# ==========================================================
# BANCO DE DADOS
# ==========================================================

def conectar():
    return sqlite3.connect(DB)

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            saldo INTEGER DEFAULT 1000,
            criado_em TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            jogo TEXT,
            aposta INTEGER,
            resultado INTEGER,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()

criar_banco()

# ==========================================================
# USUÁRIO
# ==========================================================

def criar_usuario(nome):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, saldo, criado_em)
            VALUES (?, ?, ?)
            """,
            (nome, 1000, datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass

    conn.close()


def pegar_usuario(nome):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nome, saldo FROM usuarios WHERE nome = ?",
        (nome,)
    )

    usuario = cursor.fetchone()
    conn.close()

    return usuario


def atualizar_saldo(nome, saldo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE usuarios SET saldo = ? WHERE nome = ?",
        (saldo, nome)
    )

    conn.commit()
    conn.close()


def salvar_historico(nome, jogo, aposta, resultado):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO historico
        (usuario, jogo, aposta, resultado, data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            nome,
            jogo,
            aposta,
            resultado,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        )
    )

    conn.commit()
    conn.close()

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

.stApp {
    background: #07142f;
    color: white;
}

.topo {
    background: linear-gradient(90deg, #1554d1, #2874ff);
    padding: 20px;
    border-radius: 0 0 18px 18px;
    margin-bottom: 20px;
}

.logo {
    font-size: 30px;
    font-weight: 800;
}

.saldo {
    background: #102348;
    padding: 12px 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #2853a5;
}

.banner {
    background: linear-gradient(135deg, #101f70, #40249b

import streamlit as st
import sqlite3
import random
import hashlib
import re
import html
import textwrap
from datetime import datetime

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

st.set_page_config(
    page_title="SorteClub",
    page_icon="🍀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB = "sorteclub.db"


# ==========================================================
# FUNÇÃO PARA HTML
# ==========================================================

def mostrar_html(conteudo):
    conteudo = textwrap.dedent(conteudo).strip()
    st.markdown(conteudo, unsafe_allow_html=True)


# ==========================================================
# BANCO
# ==========================================================

def conectar():
    return sqlite3.connect(DB)


def criar_banco():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            telefone TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            saldo INTEGER DEFAULT 1000,
            criado_em TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            jogo TEXT NOT NULL,
            valor INTEGER NOT NULL,
            premio INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


criar_banco()


# ==========================================================
# SEGURANÇA DA SENHA
# ==========================================================

def gerar_hash(senha):
    return hashlib.sha256(
        senha.encode("utf-8")
    ).hexdigest()


# ==========================================================
# TELEFONE
# ==========================================================

def limpar_telefone(telefone):
    return re.sub(r"\D", "", telefone)


def telefone_valido(telefone):

    telefone = limpar_telefone(telefone)

    return len(telefone) in (10, 11)


# ==========================================================
# CADASTRO
# ==========================================================

def cadastrar_usuario(usuario, telefone, senha):

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO usuarios
            (
                usuario,
                telefone,
                senha,
                saldo,
                criado_em
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            usuario,
            telefone,
            gerar_hash(senha),
            1000,
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        ))

        conn.commit()

        sucesso = True
        mensagem = "Cadastro realizado!"

    except sqlite3.IntegrityError:

        sucesso = False
        mensagem = (
            "Usuário ou telefone já cadastrado."
        )

    conn.close()

    return sucesso, mensagem


# ==========================================================
# LOGIN
# ==========================================================

def fazer_login(usuario, senha):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT usuario, saldo
        FROM usuarios
        WHERE usuario = ?
        AND senha = ?
    """, (
        usuario,
        gerar_hash(senha)
    ))

    resultado = cursor.fetchone()

    conn.close()

    return resultado


# ==========================================================
# USUÁRIO
# ==========================================================

def pegar_usuario(usuario):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT usuario, telefone, saldo
        FROM usuarios
        WHERE usuario = ?
    """, (usuario,))

    resultado = cursor.fetchone()

    conn.close()

    return resultado


def atualizar_saldo(usuario, saldo):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET saldo = ?
        WHERE usuario = ?
    """, (
        saldo,
        usuario
    ))

    conn.commit()
    conn.close()


# ==========================================================
# HISTÓRICO
# ==========================================================

def registrar_partida(
    usuario,
    jogo,
    valor,
    premio
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO partidas
        (
            usuario,
            jogo,
            valor,
            premio,
            data
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        usuario,
        jogo,
        valor,
        premio,
        datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )
    ))

    conn.commit()
    conn.close()


# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at top,
            #173c83 0%,
            #07152f 45%,
            #030914 100%
        );
    color: white;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 4rem;
    max-width: 1200px;
}

header {
    visibility: hidden;
}

/* LOGO */

.logo {
    font-size: 30px;
    font-weight: 900;
    color: white;
}

.logo-yellow {
    color: #ffd42a;
}

/* HEADER */

.topbar {
    background:
        linear-gradient(
            90deg,
            #1554d1,
            #276cf0
        );

    padding: 18px 25px;

    border-radius: 0 0 20px 20px;

    margin-bottom: 20px;
}

/* CARTEIRA */

.wallet {
    background:
        linear-gradient(
            145deg,
            #132e61,
            #0a1c3b
        );

    border: 1px solid #315ba5;

    border-radius: 16px;

    padding: 12px;

    text-align: center;
}

.wallet-title {
    font-size: 12px;
    color: #9db2d5;
}

.wallet-value {
    color: #ffd42a;
    font-size: 21px;
    font-weight: 900;
}

/* BANNER */

.banner {
    background:
        radial-gradient(
            circle at 80% 50%,
            #6139d0,
            #202d82 45%,
            #091a4a
        );

    border: 1px solid #4166bd;

    border-radius: 22px;

    padding: 30px;

    margin: 15px 0 25px;

    box-shadow:
        0 10px 30px rgba(0,0,0,.3);
}

.banner-tag {
    color: #ffd42a;
    font-weight: 900;
}

.banner-title {
    font-size: 34px;
    font-weight: 900;
    margin: 8px 0;
}

.banner-text {
    color: #c2d0eb;
}

/* CARDS */

.game-card {
    background:
        linear-gradient(
            145deg,
            #132c5b,
            #091a35
        );

    border: 1px solid #2a4e8d;

    border-radius: 20px;

    padding: 22px;

    text-align: center;

    margin-bottom: 12px;

    min-height: 205px;
}

.game-icon {
    font-size: 55px;
    margin-bottom: 10px;
}

.game-name {
    font-size: 20px;
    font-weight: 900;
}

.game-description {
    color: #9db0d2;
    font-size: 14px;
}

/* LOGIN */

.login-box {
    background:
        linear-gradient(
            145deg,
            #112958,
            #071832
        );

    border: 1px solid #31558e;

    border-radius: 25px;

    padding: 30px;

    max-width: 500px;

    margin: 30px auto;

    box-shadow:
        0 15px 40px rgba(0,0,0,.4);
}

/* FOOTER */

.footer {
    text-align: center;

    color: #7185aa;

    border-top: 1px solid #1f355d;

    padding-top: 25px;

    margin-top: 50px;

    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION
# ==========================================================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None


# ==========================================================
# TELA DE LOGIN
# ==========================================================

if not st.session_state.logado:

    mostrar_html("""
    <div class="banner">

        <div class="banner-tag">
            🍀 SORTECLUB
        </div>

        <div class="banner-title">
            Sua central de diversão
        </div>

        <div class="banner-text">
            Entre ou crie sua conta e receba
            <b>1.000 SorteCoins virtuais.</b>
        </div>

    </div>
    """)

    st.markdown(
        '<div class="login-box">',
        unsafe_allow_html=True
    )

    aba_login, aba_cadastro = st.tabs(
        [
            "🔐 Entrar",
            "📝 Criar conta"
        ]
    )

    # ======================================================
    # LOGIN
    # ======================================================

    with aba_login:

        st.subheader("🔐 Entrar")

        login_usuario = st.text_input(
            "Usuário",
            key="login_usuario"
        )

        login_senha = st.text_input(
            "Senha",
            type="password",
            key="login_senha"
        )

        if st.button(
            "🚀 ENTRAR",
            type="primary",
            use_container_width=True
        ):

            if not login_usuario or not login_senha:

                st.warning(
                    "Preencha usuário e senha."
                )

            else:

                resultado = fazer_login(
                    login_usuario,
                    login_senha
                )

                if resultado:

                    st.session_state.logado = True
                    st.session_state.usuario = (
                        resultado[0]
                    )

                    st.rerun()

                else:

                    st.error(
                        "Usuário ou senha incorretos."
                    )

    # ======================================================
    # CADASTRO
    # ======================================================

    with aba_cadastro:

        st.subheader("📝 Criar conta")

        novo_usuario = st.text_input(
            "Escolha um usuário",
            key="novo_usuario"
        )

        telefone = st.text_input(
            "Número de telefone",
            placeholder="(79) 99999-9999",
            key="telefone"
        )

        nova_senha = st.text_input(
            "Crie uma senha",
            type="password",
            key="nova_senha"
        )

        confirmar_senha = st.text_input(
            "Confirme sua senha",
            type="password",
            key="confirmar_senha"
        )

        if st.button(
            "✨ CRIAR CONTA",
            type="primary",
            use_container_width=True
        ):

            telefone_limpo = limpar_telefone(
                telefone
            )

            if not novo_usuario.strip():

                st.warning(
                    "Digite um usuário."
                )

            elif not telefone_valido(
                telefone_limpo
            ):

                st.warning(
                    "Digite um telefone válido."
                )

            elif len(nova_senha) < 6:

                st.warning(
                    "A senha precisa ter pelo menos 6 caracteres."
                )

            elif nova_senha != confirmar_senha:

                st.error(
                    "As senhas não são iguais."
                )

            else:

                sucesso, mensagem = cadastrar_usuario(
                    novo_usuario.strip(),
                    telefone_limpo,
                    nova_senha
                )

                if sucesso:

                    st.success(
                        "Conta criada! Você recebeu 1.000 SC."
                    )

                    st.info(
                        "Agora vá para a aba 'Entrar'."
                    )

                else:

                    st.error(mensagem)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    st.info(
        "🪙 SorteCoins (SC) são moedas virtuais "
        "sem valor monetário."
    )

    st.stop()


# ==========================================================
# DADOS DO USUÁRIO
# ==========================================================

dados = pegar_usuario(
    st.session_state.usuario
)

nome = dados[0]
telefone_usuario = dados[1]
saldo = dados[2]


# ==========================================================
# TOPO
# ==========================================================

col1, col2, col3 = st.columns(
    [2.5, 1.2, .7]
)

with col1:

    mostrar_html(f"""
    <div class="topbar">

        <div class="logo">
            🍀 Sorte<span class="logo-yellow">Club</span>
        </div>

        <div>
            Olá, <b>{html.escape(nome)}</b> 👋
        </div>

    </div>
    """)


with col2:

    mostrar_html(f"""
    <div class="wallet">

        <div class="wallet-title">
            SUA CARTEIRA
        </div>

        <div class="wallet-value">
            🪙 {saldo:,} SC
        </div>

    </div>
    """)


with col3:

    if st.button(
        "🚪 Sair",
        use_container_width=True
    ):

        st.session_state.logado = False
        st.session_state.usuario = None

        st.rerun()


# ==========================================================
# MENU
# ==========================================================

menu = st.radio(
    "Navegação",
    [
        "🏠 Início",
        "🎰 Jogos",
        "🎡 Roda",
        "📊 Histórico",
        "🏆 Ranking"
    ],
    horizontal=True,
    label_visibility="collapsed"
)


# ==========================================================
# INÍCIO
# ==========================================================

if menu == "🏠 Início":

    mostrar_html("""
    <div class="banner">

        <div class="banner-tag">
            🎁 BÔNUS DE BOAS-VINDAS
        </div>

        <div class="banner-title">
            Você tem 1.000 SorteCoins!
        </div>

        <div class="banner-text">
            Use suas moedas virtuais para
            experimentar os jogos da plataforma.
        </div>

    </div>
    """)

    st.subheader("🔥 Categorias")

    c1, c2, c3, c4 = st.columns(4)

    categorias = [
        ("🎰", "Slots"),
        ("🎡", "Roda"),
        ("🃏", "Cartas"),
        ("🏆", "Desafios")
    ]

    for coluna, categoria in zip(
        [c1, c2, c3, c4],
        categorias
    ):

        with coluna:

            mostrar_html(f"""
            <div class="game-card">

                <div class="game-icon">
                    {categoria[0]}
                </div>

                <div class="game-name">
                    {categoria[1]}
                </div>

            </div>
            """)


# ==========================================================
# JOGOS
# ==========================================================

elif menu == "🎰 Jogos":

    st.title("🎮 Jogos")

    st.caption(
        "Todos os jogos utilizam somente SorteCoins virtuais."
    )

    jogos = [
        ("🐯", "Tiger Fortune", "Jogo de símbolos"),
        ("🐰", "Lucky Rabbit", "Jogo de símbolos"),
        ("💎", "Lucky Gems", "Desafio de gemas"),
        ("🐲", "Dragon Luck", "Desafio do dragão"),
        ("🎡", "Crazy Wheel", "Roda da sorte"),
        ("⭐", "Star Bonus", "Bônus especial")
    ]

    colunas = st.columns(3)

    for i, jogo in enumerate(jogos):

        icone = jogo[0]
        nome_jogo = jogo[1]
        descricao = jogo[2]

        with colunas[i % 3]:

            mostrar_html(f"""
            <div class="game-card">

                <div class="game-icon">
                    {icone}
                </div>

                <div class="game-name">
                    {nome_jogo}
                </div>

                <div class="game-description">
                    {descricao}
                </div>

            </div>
            """)

            if st.button(
                f"🎮 Jogar {nome_jogo}",
                key=f"jogo_{i}",
                use_container_width=True
            ):

                st.session_state.jogo_selecionado = (
                    nome_jogo
                )

    # ======================================================
    # ÁREA DO JOGO
    # ======================================================

    if "jogo_selecionado" in st.session_state:

        jogo = st.session_state.jogo_selecionado

        st.divider()

        st.subheader(
            f"🎮 {jogo}"
        )

        valor = st.number_input(
            "Quantidade de SorteCoins",
            min_value=1,
            max_value=max(1, saldo),
            value=min(10, max(1, saldo)),
            step=1
        )

        if st.button(
            "🎯 JOGAR",
            type="primary",
            use_container_width=True
        ):

            resultados = [
                0,
                0,
                0,
                valor,
                valor * 2,
                valor * 3,
                valor * 5
            ]

            premio = random.choice(
                resultados
            )

            novo_saldo = (
                saldo - valor + premio
            )

            atualizar_saldo(
                nome,
                novo_saldo
            )

            registrar_partida(
                nome,
                jogo,
                valor,
                premio
            )

            if premio > valor:

                st.success(
                    f"🎉 Resultado: {premio:,} SC"
                )

            elif premio == valor:

                st.info(
                    f"😐 Você recuperou {premio:,} SC."
                )

            else:

                st.warning(
                    f"Resultado: {premio:,} SC."
                )

            st.rerun()


# ==========================================================
# RODA
# ==========================================================

elif menu == "🎡 Roda":

    st.title("🎡 Roda da Sorte")

    mostrar_html("""
    <div class="banner">

        <div class="banner-tag">
            🎡 CRAZY WHEEL
        </div>

        <div class="banner-title">
            Gire a roda!
        </div>

        <div class="banner-text">
            Use somente suas SorteCoins virtuais.
        </div>

    </div>
    """)

    st.markdown(
        "<div style='text-align:center;font-size:100px'>🎡</div>",
        unsafe_allow_html=True
    )

    valor = st.number_input(
        "SorteCoins utilizadas",
        min_value=1,
        max_value=max(1, saldo),
        value=min(10, max(1, saldo)),
        step=1
    )

    if st.button(
        "🎡 GIRAR A RODA",
        type="primary",
        use_container_width=True
    ):

        premios = [
            0,
            0,
            valor,
            valor * 2,
            valor * 3,
            valor * 5
        ]

        premio = random.choice(
            premios
        )

        novo_saldo = (
            saldo - valor + premio
        )

        atualizar_saldo(
            nome,
            novo_saldo
        )

        registrar_partida(
            nome,
            "Crazy Wheel",
            valor,
            premio
        )

        st.success(
            f"🎉 A roda parou em {premio:,} SC!"
        )

        st.rerun()


# ==========================================================
# HISTÓRICO
# ==========================================================

elif menu == "📊 Histórico":

    st.title("📊 Histórico")

    conn = conectar()

    partidas = conn.execute("""
        SELECT
            jogo,
            valor,
            premio,
            data
        FROM partidas
        WHERE usuario = ?
        ORDER BY id DESC
        LIMIT 50
    """, (nome,)).fetchall()

    conn.close()

    if not partidas:

        st.info(
            "Nenhuma partida realizada ainda."
        )

else:
                    

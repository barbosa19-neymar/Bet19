import streamlit as st
import sqlite3
import random
from datetime import datetime

# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="SorteClub",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB = "sorteclub.db"

# =========================================================
# BANCO DE DADOS
# =========================================================

def conectar():
    return sqlite3.connect(DB)


def criar_banco():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            saldo INTEGER DEFAULT 1000,
            criado_em TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            jogo TEXT,
            valor INTEGER,
            premio INTEGER,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()


criar_banco()


# =========================================================
# USUÁRIOS
# =========================================================

def criar_usuario(nome):

    conn = conectar()
    cur = conn.cursor()

    cur.execute(
        "SELECT nome FROM usuarios WHERE nome = ?",
        (nome,)
    )

    existe = cur.fetchone()

    if not existe:
        cur.execute("""
            INSERT INTO usuarios
            (nome, saldo, criado_em)
            VALUES (?, ?, ?)
        """, (
            nome,
            1000,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        ))

    conn.commit()
    conn.close()


def pegar_usuario(nome):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT nome, saldo
        FROM usuarios
        WHERE nome = ?
    """, (nome,))

    resultado = cur.fetchone()

    conn.close()

    return resultado


def alterar_saldo(nome, novo_saldo):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        UPDATE usuarios
        SET saldo = ?
        WHERE nome = ?
    """, (novo_saldo, nome))

    conn.commit()
    conn.close()


def registrar_partida(
    usuario,
    jogo,
    valor,
    premio
):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO partidas
        (usuario, jogo, valor, premio, data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        usuario,
        jogo,
        valor,
        premio,
        datetime.now().strftime("%d/%m/%Y %H:%M")
    ))

    conn.commit()
    conn.close()


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at top,
            #173c83 0%,
            #07152f 42%,
            #040b1b 100%
        );
    color: white;
}

/* Remove margem superior */

.block-container {
    padding-top: 1rem;
    padding-bottom: 4rem;
}

/* CABEÇALHO */

.header {
    background: linear-gradient(
        90deg,
        #1554d1,
        #2868ed
    );

    padding: 18px 25px;

    border-radius: 0 0 20px 20px;

    box-shadow:
        0 8px 30px rgba(0,0,0,.25);

    margin-bottom: 20px;
}

.logo {
    font-size: 29px;
    font-weight: 900;
}

.logo span {
    color: #ffd52e;
}

/* SALDO */

.wallet {
    background: linear-gradient(
        135deg,
        #132e61,
        #0b1d3d
    );

    border: 1px solid #315ba5;

    border-radius: 15px;

    padding: 13px;

    text-align: center;
}

.wallet-title {
    color: #9eb4dd;
    font-size: 13px;
}

.wallet-value {
    color: #ffd42a;
    font-size: 22px;
    font-weight: 900;
}

/* BANNER */

.banner {
    background:
        radial-gradient(
            circle at right,
            #5734c8,
            #182d7d 45%,
            #091a4a
        );

    border-radius: 22px;

    padding: 35px;

    min-height: 190px;

    border: 1px solid #375db0;

    box-shadow:
        0 10px 35px rgba(0,0,0,.35);

    margin: 15px 0 25px;
}

.banner-small {
    color: #ffda2d;
    font-weight: 800;
    font-size: 15px;
}

.banner h1 {
    font-size: 36px;
    margin: 8px 0;
}

.banner p {
    color: #c9d5ef;
    font-size: 16px;
}

/* CATEGORIAS */

.category {
    background: #10234a;

    border: 1px solid #27457c;

    border-radius: 15px;

    padding: 15px;

    text-align: center;

    margin-bottom: 20px;

    font-weight: 700;
}

.category:hover {
    border-color: #ffd42a;
}

/* CARDS */

.game-card {
    background: linear-gradient(
        145deg,
        #132b58,
        #091936
    );

    border-radius: 20px;

    border: 1px solid #294a83;

    padding: 20px;

    text-align: center;

    min-height: 230px;

    box-shadow:
        0 8px 25px rgba(0,0,0,.25);

    margin-bottom: 15px;
}

.game-icon {
    font-size: 58px;
}

.game-title {
    font-size: 21px;
    font-weight: 900;
}

.game-description {
    color: #9eb0d0;
    font-size: 14px;
}

/* ÁREA DO JOGO */

.game-area {
    background: #091936;

    border: 1px solid #27477f;

    border-radius: 20px;

    padding: 25px;

    margin-top: 20px;
}

/* RODA */

.wheel {
    font-size: 110px;
    text-align: center;
    padding: 25px;
}

/* RODAPÉ */

.footer {
    margin-top: 50px;

    padding: 25px;

    text-align: center;

    color: #687da7;

    border-top: 1px solid #20365f;

    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOGIN
# =========================================================

if "usuario" not in st.session_state:
    st.session_state.usuario = None


if st.session_state.usuario is None:

    st.markdown("""
    <div class="banner">

        <div class="banner-small">
            🎁 BÔNUS DE BOAS-VINDAS
        </div>

        <h1>Bem-vindo ao SorteClub!</h1>

        <p>
            Entre na plataforma e receba
            <b>1.000 SorteCoins</b> virtuais.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.subheader("👤 Criar jogador")

    nome = st.text_input(
        "Nome de usuário",
        placeholder="Digite seu nome"
    )

    if st.button(
        "🚀 ENTRAR NO SORTECLUB",
        use_container_width=True
    ):

        if nome.strip():

            nome = nome.strip()

            criar_usuario(nome)

            st.session_state.usuario = nome

            st.rerun()

        else:

            st.warning(
                "Digite um nome para entrar."
            )

    st.info(
        "SorteCoins são moedas virtuais utilizadas "
        "somente dentro desta demonstração."
    )

    st.stop()


# =========================================================
# DADOS
# =========================================================

usuario = pegar_usuario(
    st.session_state.usuario
)

nome = usuario[0]
saldo = usuario[1]


# =========================================================
# CABEÇALHO
# =========================================================

col1, col2, col3 = st.columns(
    [2.5, 1.2, .7]
)

with col1:

    st.markdown(f"""
    <div class="header">

        <div class="logo">
            🍀 Sorte<span>Club</span>
        </div>

        <div>
            Olá, <b>{nome}</b> 👋
        </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown(f"""
    <div class="wallet">

        <div class="wallet-title">
            SUA CARTEIRA
        </div>

        <div class="wallet-value">
            🪙 {saldo:,} SC
        </div>

    </div>
    """, unsafe_allow_html=True)


with col3:

    if st.button(
        "🚪 Sair",
        use_container_width=True
    ):

        st.session_state.usuario = None

        st.rerun()


# =========================================================
# MENU
# =========================================================

menu = st.radio(
    "",
    [
        "🏠 Início",
        "🎰 Jogos",
        "🎡 Roda",
        "📊 Histórico",
        "🏆 Ranking"
    ],
    horizontal=True
)


# =========================================================
# INÍCIO
# =========================================================

if menu == "🏠 Início":

    st.markdown("""
    <div class="banner">

        <div class="banner-small">
            🎁 SORTECOINS VIRTUAIS
        </div>

        <h1>
            Comece com 1.000 SC!
        </h1>

        <p>
            Explore os jogos e divirta-se
            utilizando a moeda interna da plataforma.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.subheader("🔥 Categorias")

    categorias = [
        ("🎰", "Slots"),
        ("🎡", "Roda"),
        ("🃏", "Cartas"),
        ("🏆", "Desafios")
    ]

    cols = st.columns(4)

    for col, categoria in zip(
        cols,
        categorias
    ):

        with col:

            st.markdown(
                f"""
                <div class="category">

                    <div style="font-size:30px">
                        {categoria[0]}
                    </div>

                    {categoria[1]}

                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# JOGOS
# =========================================================

elif menu == "🎰 Jogos":

    st.title("🎮 Jogos")

    st.caption(
        "Todos os jogos utilizam somente SorteCoins virtuais."
    )

    jogos = [

        (
            "🐯",
            "Tiger Fortune",
            "Jogo de símbolos"
        ),

        (
            "🐰",
            "Lucky Rabbit",
            "Combine símbolos"
        ),

        (
            "💎",
            "Lucky Gems",
            "Encontre os bônus"
        ),

        (
            "🐲",
            "Dragon Luck",
            "Desafio do dragão"
        ),

        (
            "🎡",
            "Crazy Wheel",
            "Gire a roda"
        ),

        (
            "⭐",
            "Star Bonus",
            "Desafio especial"
        )
    ]

    cols = st.columns(3)

    for i, jogo in enumerate(jogos):

        with cols[i % 3]:

            st.markdown(f"""
            <div class="game-card">

                <div class="game-icon">
                    {jogo[0]}
                </div>

                <div class="game-title">
                    {jogo[1]}
                </div>

                <div class="game-description">
                    {jogo[2]}
                </div>

            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"Jogar {jogo[1]}",
                key=f"game_{i}",
                use_container_width=True
            ):

                st.session_state.jogo = jogo[1]


# =========================================================
# JOGO
# =========================================================

if "jogo" in st.session_state:

    jogo = st.session_state.jogo

    st.markdown(
        f"""
        <div class="game-area">

            <h2>
                🎮 {jogo}
            </h2>

            <p>
                Utilize suas SorteCoins para jogar.
            </p>

        </div>
        """,
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
        "🎯 JOGAR AGORA",
        type="primary",
        use_container_width=True
    ):

        # Resultado fictício
        opcoes = [
            0,
            0,
            0,
            valor,
            valor * 2,
            valor * 3,
            valor * 5
        ]

        premio = random.choice(opcoes)

        novo_saldo = saldo - valor + premio

        alterar_saldo(
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
                f"🎉 Você recebeu {premio:,} SC!"
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


# =========================================================
# RODA
# =========================================================

elif menu == "🎡 Roda":

    st.title("🎡 Roda da Sorte")

    st.markdown(
        '<div class="wheel">🎡</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="banner">

        <div class="banner-small">
            CRAZY WHEEL
        </div>

        <h1>
            Gire e descubra seu prêmio!
        </h1>

        <p>
            Moedas exclusivamente virtuais.
        </p>

    </div>
    """, unsafe_allow_html=True)

    valor = st.number_input(
        "SorteCoins utilizadas",
        min_value=1,
        max_value=max(1, saldo),
        value=min(10, max(1, saldo))
    )

    if st.button(
        "🎡 GIRAR",
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

        premio = random.choice(premios)

        novo_saldo = saldo - valor + premio

        alterar_saldo(
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


# =========================================================
# HISTÓRICO
# =========================================================

elif menu == "📊 Histórico":

    st.title("📊 Histórico")

    conn = conectar()

    dados = conn.execute("""
        SELECT jogo, valor, premio, data
        FROM partidas
        WHERE usuario = ?
        ORDER BY id DESC
        LIMIT 50
    """, (nome,)).fetchall()

    conn.close()

    if not dados:

        st.info(
            "Você ainda não jogou nenhuma partida."
        )

    else:

        for jogo, valor, premio, data in dados:

            diferenca = premio - valor

            if diferenca > 0:
                icone = "🟢"
            elif diferenca < 0:
                icone = "🔴"
            else:
                icone = "⚪"

            st.markdown(f"""
            <div class="game-card">

                <h3>
                    {icone} {jogo}
                </h3>

                <p>
                    Usado: {valor:,} SC
                    &nbsp; | &nbsp;
                    Resultado: {premio:,} SC
                </p>

                <small>
                    {data}
                </small>

            </div>
            """, unsafe_allow_html=True)


# =========================================================
# RANKING
# =========================================================

elif menu == "🏆 Ranking":

    st.title("🏆 Ranking dos jogadores")

    conn = conectar()

    ranking = conn.execute("""
        SELECT nome, saldo
        FROM usuarios
        ORDER BY saldo DESC
        LIMIT 20
    """).fetchall()

    conn.close()

    for posicao, jogador in enumerate(
        ranking,
        start=1
    ):

        nome_rank = jogador[0]
        saldo_rank = jogador[1]

        if posicao == 1:
            medalha = "🥇"
        elif posicao == 2:
            medalha = "🥈"
        elif posicao == 3:
            medalha = "🥉"
        else:
            medalha = f"#{posicao}"

        st.markdown(f"""
        <div class="game-card">

            <h2>
                {medalha} {nome_rank}
            </h2>

            <p>
                🪙 {saldo_rank:,} SC
            </p>

        </div>
        """, unsafe_allow_html=True)


# =========================================================
# RODAPÉ
# =========================================================

st.markdown("""
<div class="footer">

    🍀 SorteClub — Projeto demonstrativo

    <br><br>

    SC = SorteCoins, moeda virtual interna.
    <br>
    Não possui valor monetário e não pode ser
    convertida, depositada ou sacada.

</div>
""", unsafe_allow_html=True)

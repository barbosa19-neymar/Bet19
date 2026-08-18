
import streamlit as st
import sqlite3
import hashlib
import random
import re
from datetime import datetime

st.set_page_config(page_title="SorteClub", page_icon="🍀", layout="wide")
DB = "sorteclub.db"

def db():
    return sqlite3.connect(DB)

def init_db():
    c = db()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            telefone TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            saldo INTEGER NOT NULL DEFAULT 1000
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS partidas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            jogo TEXT NOT NULL,
            aposta INTEGER NOT NULL,
            premio INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    """)
    c.commit()
    c.close()

def senha_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

def telefone_ok(t):
    return len(re.sub(r"\D", "", t)) in (10, 11)

def cadastrar(usuario, telefone, senha):
    c = db()
    try:
        c.execute(
            "INSERT INTO usuarios(usuario,telefone,senha,saldo) VALUES(?,?,?,1000)",
            (usuario, re.sub(r"\D", "", telefone), senha_hash(senha))
        )
        c.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False
    c.close()
    return ok

def login(usuario, senha):
    c = db()
    row = c.execute(
        "SELECT usuario FROM usuarios WHERE usuario=? AND senha=?",
        (usuario, senha_hash(senha))
    ).fetchone()
    c.close()
    return row is not None

def saldo(usuario):
    c = db()
    row = c.execute("SELECT saldo FROM usuarios WHERE usuario=?", (usuario,)).fetchone()
    c.close()
    return row[0] if row else 0

def alterar_saldo(usuario, valor):
    c = db()
    c.execute("UPDATE usuarios SET saldo=? WHERE usuario=?", (valor, usuario))
    c.commit()
    c.close()

def registrar(usuario, jogo, aposta, premio):
    c = db()
    c.execute(
        "INSERT INTO partidas(usuario,jogo,aposta,premio,data) VALUES(?,?,?,?,?)",
        (usuario, jogo, aposta, premio, datetime.now().strftime("%d/%m/%Y %H:%M"))
    )
    c.commit()
    c.close()

init_db()

st.markdown("""
<style>
.stApp { background:#07152f; color:white; }
.block-container { max-width:1200px; padding-top:1rem; }
.hero {
    background:linear-gradient(135deg,#172f82,#5427a8);
    padding:30px; border-radius:22px; margin:15px 0 25px;
}
.card {
    background:#10254b; border:1px solid #2b4f8d;
    border-radius:18px; padding:22px; text-align:center;
    margin-bottom:15px;
}
.coin { color:#ffd42a; font-weight:900; font-size:21px; }
.game-icon { font-size:55px; }
.small { color:#aebfdf; }
</style>
""", unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if not st.session_state.logado:
    st.markdown("""
    <div class="hero">
        <h1>🍀 SorteClub</h1>
        <p>Plataforma de jogos com moedas virtuais.</p>
        <b>🎁 Ganhe 1.000 SorteCoins ao criar sua conta.</b>
    </div>
    """, unsafe_allow_html=True)

    login_tab, cadastro_tab = st.tabs(["🔐 Entrar", "📝 Cadastrar"])

    with login_tab:
        u = st.text_input("Usuário", key="login_u")
        p = st.text_input("Senha", type="password", key="login_p")
        if st.button("ENTRAR", type="primary", use_container_width=True):
            if login(u.strip(), p):
                st.session_state.logado = True
                st.session_state.usuario = u.strip()
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with cadastro_tab:
        u = st.text_input("Novo usuário", key="cad_u")
        t = st.text_input("Telefone", placeholder="(79) 99999-9999", key="cad_t")
        p1 = st.text_input("Senha", type="password", key="cad_p1")
        p2 = st.text_input("Confirmar senha", type="password", key="cad_p2")

        if st.button("CRIAR CONTA", type="primary", use_container_width=True):
            if not u.strip() or not t or not p1:
                st.warning("Preencha todos os campos.")
            elif not telefone_ok(t):
                st.warning("Digite um telefone válido.")
            elif len(p1) < 6:
                st.warning("A senha precisa ter pelo menos 6 caracteres.")
            elif p1 != p2:
                st.error("As senhas não são iguais.")
            elif cadastrar(u.strip(), t, p1):
                st.success("Conta criada! Você recebeu 1.000 SorteCoins.")
            else:
                st.error("Usuário ou telefone já cadastrado.")

    st.info("SorteCoins são moedas virtuais sem valor monetário.")
    st.stop()

usuario = st.session_state.usuario
sc = saldo(usuario)

a, b, c = st.columns([2, 1, 0.7])

with a:
    st.markdown(
        f'<div class="hero"><h2>🍀 SorteClub</h2><p>Olá, <b>{usuario}</b> 👋</p></div>',
        unsafe_allow_html=True
    )

with b:
    st.markdown(
        f'<div class="card">🪙<br><span class="coin">{sc:,} SC</span></div>',
        unsafe_allow_html=True
    )

with c:
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.rerun()

menu = st.radio(
    "Menu",
    ["🏠 Início", "🎰 Jogos", "🎡 Roda", "📊 Histórico", "🏆 Ranking"],
    horizontal=True,
    label_visibility="collapsed"
)

if menu == "🏠 Início":
    st.markdown("""
    <div class="hero">
        <h1>🎁 Bônus de boas-vindas</h1>
        <p>Você começa com <b>1.000 SorteCoins</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🔥 Categorias")
    cols = st.columns(4)

    for col, icon, name in zip(
        cols,
        ["🎰", "🎡", "🃏", "🏆"],
        ["Slots", "Roda", "Cartas", "Desafios"]
    ):
        with col:
            st.markdown(
                f'<div class="card"><div class="game-icon">{icon}</div><h3>{name}</h3></div>',
                unsafe_allow_html=True
            )

elif menu == "🎰 Jogos":
    st.title("🐯 Tiger Fortune")
    st.caption("Slot fictício de entretenimento — usa somente pontos virtuais.")

    if "tf_points" not in st.session_state:
        st.session_state.tf_points = 1000
    if "tf_reels" not in st.session_state:
        st.session_state.tf_reels = [
            ["🐯", "💎", "7️⃣"],
            ["🍒", "🐯", "⭐"],
            ["💰", "🔔", "🐯"],
        ]
    if "tf_message" not in st.session_state:
        st.session_state.tf_message = "Clique em GIRAR para começar!"

    st.markdown("""
    <style>
    .tf-wrap {
        background: linear-gradient(180deg,#17102a,#2a1238 55%,#120b1d);
        border: 2px solid #d7a72a;
        border-radius: 26px;
        padding: 24px;
        box-shadow: 0 12px 40px rgba(0,0,0,.35);
        max-width: 900px;
        margin: auto;
    }
    .tf-title {
        text-align:center;
        color:#ffd75a;
        font-size:42px;
        font-weight:900;
        text-shadow:0 3px 0 #6d3b00;
        margin-bottom:4px;
    }
    .tf-subtitle {
        text-align:center;
        color:#fff2bd;
        margin-bottom:20px;
    }
    .tf-reel {
        background:linear-gradient(180deg,#fff8dc,#e9d59b);
        border:4px solid #d29b21;
        border-radius:16px;
        height:115px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:55px;
        margin:5px;
        box-shadow: inset 0 0 15px rgba(0,0,0,.25);
    }
    .tf-win {
        text-align:center;
        color:#ffe66b;
        font-size:25px;
        font-weight:900;
        padding:12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tf-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="tf-title">🐯 TIGER FORTUNE 🐯</div>', unsafe_allow_html=True)
    st.markdown('<div class="tf-subtitle">5 símbolos • 3 linhas • pontos virtuais</div>', unsafe_allow_html=True)

    # Show the three visible rows of the 3-reel game.
    for row in range(3):
        cols = st.columns(3)
        for col, reel in zip(cols, st.session_state.tf_reels):
            with col:
                st.markdown(
                    f'<div class="tf-reel">{reel[row]}</div>',
                    unsafe_allow_html=True
                )

    st.markdown(
        f'<div class="tf-win">{st.session_state.tf_message}</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    a, b, c = st.columns([1, 1.2, 1])
    with a:
        st.metric("⭐ Pontos", f"{st.session_state.tf_points:,}")
    with b:
        girar = st.button("🐯 GIRAR", type="primary", use_container_width=True)
    with c:
        reset = st.button("🔄 Reiniciar", use_container_width=True)

    if reset:
        st.session_state.tf_points = 1000
        st.session_state.tf_message = "Pronto para jogar!"
        st.rerun()

    if girar:
        symbols = ["🐯", "💎", "7️⃣", "🍒", "⭐", "💰", "🔔", "🪙"]
        reels = [
            [random.choice(symbols) for _ in range(3)],
            [random.choice(symbols) for _ in range(3)],
            [random.choice(symbols) for _ in range(3)],
        ]
        st.session_state.tf_reels = reels

        # Score-only rules: no wager, no cash value.
        rows = [reels[0][r] + reels[1][r] + reels[2][r] for r in range(3)]
        tiger = sum(row.count("🐯") for row in rows)
        triples = sum(1 for row in rows if row[0] == row[1] == row[2])

        points = 0
        if triples:
            points += 100
        if tiger >= 2:
            points += 50
        if "💎" in "".join(rows):
            points += 10

        st.session_state.tf_points += points

        if triples:
            st.session_state.tf_message = f"🔥 TRINCA! +{points} pontos"
        elif tiger >= 2:
            st.session_state.tf_message = f"🐯 TIGRES! +{points} pontos"
        elif points:
            st.session_state.tf_message = f"✨ Bônus! +{points} pontos"
        else:
            st.session_state.tf_message = "Tente novamente! +0 pontos"

        st.rerun()

    st.info("Este Tiger Fortune é uma versão fictícia e usa somente pontos virtuais; não há apostas, depósitos ou saques.")


elif menu == "🎡 Roda":
    st.title("🎡 Roda da Sorte")

    st.markdown(
        '<div style="text-align:center;font-size:100px">🎡</div>',
        unsafe_allow_html=True
    )

    aposta = st.number_input(
        "SorteCoins para usar",
        min_value=1,
        max_value=max(1, sc),
        value=min(10, max(1, sc))
    )

    if st.button(
        "GIRAR A RODA",
        type="primary",
        use_container_width=True
    ):
        premio = random.choice(
            [0, 0, aposta, aposta * 2, aposta * 3, aposta * 5]
        )

        alterar_saldo(
            usuario,
            sc - aposta + premio
        )

        registrar(
            usuario,
            "Crazy Wheel",
            aposta,
            premio
        )

        st.success(
            f"A roda parou em {premio:,} SC!"
        )

        st.rerun()

elif menu == "📊 Histórico":
    st.title("📊 Histórico")

    c = db()
    rows = c.execute(
        """
        SELECT jogo, aposta, premio, data
        FROM partidas
        WHERE usuario=?
        ORDER BY id DESC
        LIMIT 50
        """,
        (usuario,)
    ).fetchall()
    c.close()

    if not rows:
        st.info("Nenhuma partida ainda.")

    for jogo, aposta, premio, data in rows:
        emoji = "🟢" if premio > aposta else "🔴" if premio < aposta else "⚪"

        st.markdown(
            f'<div class="card"><h3>{emoji} {jogo}</h3>'
            f'<p>Usado: {aposta:,} SC | Resultado: {premio:,} SC</p>'
            f'<span class="small">{data}</span></div>',
            unsafe_allow_html=True
        )

elif menu == "🏆 Ranking":
    st.title("🏆 Ranking")

    c = db()
    rows = c.execute(
        "SELECT usuario, saldo FROM usuarios ORDER BY saldo DESC LIMIT 20"
    ).fetchall()
    c.close()

    for i, (nome, valor) in enumerate(rows, 1):
        medalha = (
            "🥇" if i == 1
            else "🥈" if i == 2
            else "🥉" if i == 3
            else f"#{i}"
        )

        st.markdown(
            f'<div class="card"><h3>{medalha} {nome}</h3>'
            f'<div class="coin">🪙 {valor:,} SC</div></div>',
            unsafe_allow_html=True
        )

st.markdown(
    '<p style="text-align:center;color:#7185aa;margin-top:40px">'
    'SorteCoins são moedas virtuais sem valor monetário.</p>',
    unsafe_allow_html=True
)

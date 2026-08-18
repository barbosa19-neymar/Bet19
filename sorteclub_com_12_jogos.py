
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
    st.title("🎮 Jogos")
    st.caption("Todos os jogos utilizam somente SorteCoins virtuais.")

    jogos = [
        ("🐯", "Tiger Fortune", "Caça aos símbolos"),
        ("🐰", "Lucky Rabbit", "Combine símbolos"),
        ("💎", "Lucky Gems", "Encontre a gema"),
        ("🐲", "Dragon Luck", "Desafio das portas"),
        ("⭐", "Star Bonus", "Bônus de estrelas"),
        ("🎯", "Lucky Target", "Acerte o alvo"),
        ("🍒", "Fruit Match", "Combine frutas"),
        ("🦁", "Lion Gold", "Desafio do leão"),
        ("🐼", "Panda Spin", "Giro de pontuação"),
        ("🔥", "Fire Bonus", "Rodada de bônus"),
        ("🌊", "Ocean Treasure", "Tesouro escondido"),
        ("👑", "Royal Match", "Combine símbolos reais")
    ]

    cols = st.columns(3)

    for i, (icon, name, desc) in enumerate(jogos):
        with cols[i % 3]:
            st.markdown(
                f'<div class="card"><div class="game-icon">{icon}</div><h3>{name}</h3><p class="small">{desc}</p></div>',
                unsafe_allow_html=True
            )

            if st.button(
                f"Jogar {name}",
                key=f"g{i}",
                use_container_width=True
            ):
                st.session_state.jogo = name
                st.session_state.rodada = 0
                st.session_state.pontos_jogo = 0
                st.rerun()

    if "jogo" in st.session_state:
        st.divider()
        st.subheader(f"🎮 {st.session_state.jogo}")
        st.caption("Jogo gratuito de pontos — sem aposta ou dinheiro real.")

        if "rodada" not in st.session_state:
            st.session_state.rodada = 0
        if "pontos_jogo" not in st.session_state:
            st.session_state.pontos_jogo = 0

        # Jogos diferentes com uma ação realmente jogável.
        if st.session_state.jogo in ["Tiger Fortune", "Lucky Rabbit", "Lucky Gems"]:
            opcoes = {
                "Tiger Fortune": ["🐯", "🦁", "🐯", "🐰", "🐯"],
                "Lucky Rabbit": ["🐰", "🥕", "🐰", "⭐", "🐇"],
                "Lucky Gems": ["💎", "💎", "🔷", "⭐", "💎"],
            }
            alvo = random.choice(opcoes[st.session_state.jogo])
            st.markdown(
                '<div class="card"><div class="game-icon">🎰</div>'
                '<h3>Escolha um símbolo</h3></div>',
                unsafe_allow_html=True
            )

            escolhas = list(dict.fromkeys(opcoes[st.session_state.jogo]))
            cols_game = st.columns(len(escolhas))
            for j, simbolo in enumerate(escolhas):
                with cols_game[j]:
                    if st.button(simbolo, key=f"play_{st.session_state.rodada}_{j}",
                                 use_container_width=True):
                        st.session_state.rodada += 1
                        if simbolo == alvo:
                            st.session_state.pontos_jogo += 10
                            st.success(f"🎉 Acertou! Era {alvo}. +10 pontos")
                        else:
                            st.info(f"Quase! O símbolo sorteado foi {alvo}.")
                        st.rerun()

        elif st.session_state.jogo == "Dragon Luck":
            st.markdown(
                '<div class="card"><div class="game-icon">🐲</div>'
                '<h3>Desafio do Dragão</h3><p>Escolha uma porta!</p></div>',
                unsafe_allow_html=True
            )
            portas = ["🚪 1", "🚪 2", "🚪 3"]
            dragao = random.choice(portas)
            cols_game = st.columns(3)
            for j, porta in enumerate(portas):
                with cols_game[j]:
                    if st.button(porta, key=f"dragon_{st.session_state.rodada}_{j}",
                                 use_container_width=True):
                        st.session_state.rodada += 1
                        if porta == dragao:
                            st.session_state.pontos_jogo += 15
                            st.success("🐲 Você encontrou o dragão! +15 pontos")
                        else:
                            st.info(f"Não foi dessa vez. O dragão estava na {dragao}.")
                        st.rerun()

        elif st.session_state.jogo == "Star Bonus":
            st.markdown(
                '<div class="card"><div class="game-icon">⭐</div>'
                '<h3>Caça às Estrelas</h3><p>Clique para tentar encontrar uma estrela.</p></div>',
                unsafe_allow_html=True
            )
            if st.button("✨ TENTAR", type="primary", use_container_width=True):
                st.session_state.rodada += 1
                achou = random.random() < 0.35
                if achou:
                    st.session_state.pontos_jogo += 20
                    st.success("⭐ Você encontrou uma estrela! +20 pontos")
                else:
                    st.info("☁️ Não apareceu estrela. Tente novamente!")
                st.rerun()

        elif st.session_state.jogo == "Fruit Match":
            st.markdown('<div class="card"><div class="game-icon">🍒</div><h3>Fruit Match</h3><p>Escolha uma fruta e tente encontrar a fruta especial.</p></div>', unsafe_allow_html=True)
            frutas = ["🍒", "🍋", "🍉", "🍇", "🍎"]
            especial = random.choice(frutas)
            cols_game = st.columns(len(frutas))
            for j, fruta in enumerate(frutas):
                with cols_game[j]:
                    if st.button(fruta, key=f"fruit_{st.session_state.rodada}_{j}", use_container_width=True):
                        st.session_state.rodada += 1
                        if fruta == especial:
                            st.session_state.pontos_jogo += 15
                            st.success(f"🍓 Acertou! +15 pontos")
                        else:
                            st.info("Essa fruta não era a especial.")
                        st.rerun()

        elif st.session_state.jogo == "Lion Gold":
            st.markdown('<div class="card"><div class="game-icon">🦁</div><h3>Lion Gold</h3><p>Escolha uma das três cartas.</p></div>', unsafe_allow_html=True)
            cartas = ["🃏 A", "🃏 B", "🃏 C"]
            premio = random.choice(cartas)
            cols_game = st.columns(3)
            for j, carta in enumerate(cartas):
                with cols_game[j]:
                    if st.button(carta, key=f"lion_{st.session_state.rodada}_{j}", use_container_width=True):
                        st.session_state.rodada += 1
                        if carta == premio:
                            st.session_state.pontos_jogo += 25
                            st.success("🦁 Você encontrou a carta dourada! +25 pontos")
                        else:
                            st.info(f"A carta dourada estava em {premio}.")
                        st.rerun()

        elif st.session_state.jogo == "Panda Spin":
            st.markdown('<div class="card"><div class="game-icon">🐼</div><h3>Panda Spin</h3><p>Gire a roda para ganhar pontos virtuais.</p></div>', unsafe_allow_html=True)
            if st.button("🔄 GIRAR", type="primary", use_container_width=True):
                valores = [0, 5, 10, 15, 20, 30]
                ganho = random.choice(valores)
                st.session_state.rodada += 1
                st.session_state.pontos_jogo += ganho
                st.success(f"🐼 Você ganhou {ganho} pontos!")
                st.rerun()

        elif st.session_state.jogo == "Fire Bonus":
            st.markdown('<div class="card"><div class="game-icon">🔥</div><h3>Fire Bonus</h3><p>Escolha uma chama para descobrir o bônus.</p></div>', unsafe_allow_html=True)
            chamas = ["🔥 1", "🔥 2", "🔥 3", "🔥 4"]
            cols_game = st.columns(4)
            especial = random.choice(chamas)
            for j, chama in enumerate(chamas):
                with cols_game[j]:
                    if st.button(chama, key=f"fire_{st.session_state.rodada}_{j}", use_container_width=True):
                        st.session_state.rodada += 1
                        if chama == especial:
                            st.session_state.pontos_jogo += 30
                            st.success("🔥 BÔNUS! +30 pontos")
                        else:
                            st.info("A chama bônus estava em outro lugar.")
                        st.rerun()

        elif st.session_state.jogo == "Ocean Treasure":
            st.markdown('<div class="card"><div class="game-icon">🌊</div><h3>Ocean Treasure</h3><p>Procure o baú escondido.</p></div>', unsafe_allow_html=True)
            baus = ["🧰 1", "🧰 2", "🧰 3", "🧰 4"]
            tesouro = random.choice(baus)
            cols_game = st.columns(4)
            for j, bau in enumerate(baus):
                with cols_game[j]:
                    if st.button(bau, key=f"ocean_{st.session_state.rodada}_{j}", use_container_width=True):
                        st.session_state.rodada += 1
                        if bau == tesouro:
                            st.session_state.pontos_jogo += 35
                            st.success("💰 Tesouro encontrado! +35 pontos")
                        else:
                            st.info("Esse baú estava vazio.")
                        st.rerun()

        elif st.session_state.jogo == "Royal Match":
            st.markdown('<div class="card"><div class="game-icon">👑</div><h3>Royal Match</h3><p>Escolha o símbolo real correto.</p></div>', unsafe_allow_html=True)
            simbolos = ["👑", "💎", "🏰", "🛡️", "⭐"]
            alvo = random.choice(simbolos)
            cols_game = st.columns(len(simbolos))
            for j, simbolo in enumerate(simbolos):
                with cols_game[j]:
                    if st.button(simbolo, key=f"royal_{st.session_state.rodada}_{j}", use_container_width=True):
                        st.session_state.rodada += 1
                        if simbolo == alvo:
                            st.session_state.pontos_jogo += 25
                            st.success("👑 Combinação perfeita! +25 pontos")
                        else:
                            st.info(f"O símbolo correto era {alvo}.")
                        st.rerun()

        else:  # Lucky Target
            st.markdown(
                '<div class="card"><div class="game-icon">🎯</div>'
                '<h3>Lucky Target</h3><p>Tente chegar o mais perto possível de 50.</p></div>',
                unsafe_allow_html=True
            )
            if st.button("🎯 LANÇAR", type="primary", use_container_width=True):
                numero = random.randint(1, 100)
                st.session_state.rodada += 1
                distancia = abs(50 - numero)
                ganho = max(0, 20 - distancia // 3)
                st.session_state.pontos_jogo += ganho
                st.success(f"🎯 Saiu {numero}! Você ganhou {ganho} pontos.")
                st.rerun()

        st.metric("🏆 Pontos nesta sessão", st.session_state.pontos_jogo)
        if st.button("⬅️ Escolher outro jogo", use_container_width=True):
            del st.session_state["jogo"]
            st.session_state.pop("rodada", None)
            st.session_state.pop("pontos_jogo", None)
            st.rerun()

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

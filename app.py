# app.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from typing import List, Dict

st.set_page_config(page_title="Loja de Livros", page_icon="📚", layout="wide")

# ---------- Helpers ----------
def init_state():
    # view_mode: "Lista" | "Grade"
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "Lista"
    # boolean dedicado ao toggle para evitar colisão de tipos
    if "view_toggle" not in st.session_state:
        st.session_state.view_toggle = False
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    if "page" not in st.session_state:
        st.session_state.page = 1

@st.cache_data
def load_books() -> List[Dict]:
    import json, pathlib
    data_path = pathlib.Path("books.json")
    if not data_path.exists():
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def money(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def add_to_cart(book_id: str, price: float):
    cart = st.session_state.cart
    item = cart.get(book_id, {"qty": 0, "price": price})
    item["qty"] += 1
    item["price"] = price
    cart[book_id] = item

def remove_from_cart(book_id: str):
    cart = st.session_state.cart
    if book_id in cart:
        cart[book_id]["qty"] -= 1
        if cart[book_id]["qty"] <= 0:
            del cart[book_id]

def cart_summary(books_map: Dict[str, Dict]):
    total = 0.0
    q = 0
    for book_id, item in st.session_state.cart.items():
        total += item["qty"] * item["price"]
        q += item["qty"]
    st.markdown(f"**Itens no carrinho:** {q}  \n**Total:** {money(total)}")
    if st.session_state.cart:
        for book_id, item in st.session_state.cart.items():
            b = books_map.get(book_id, {})
            col1, col2, col3 = st.columns([6, 2, 2])
            with col1:
                st.caption(b.get("author", ""))
                st.write(f"**{b.get('title', '')}**")
            with col2:
                st.write(f"{item['qty']} un.")
            with col3:
                if st.button("Remover", key=f"rm_{book_id}"):
                    remove_from_cart(book_id)
                    st.rerun()
        st.divider()
        st.button("Finalizar compra", type="primary")
    else:
        st.caption("Seu carrinho está vazio.")

def book_card(b: Dict, in_list=True):
    # Card
    with st.container(border=True):
        if in_list:
            c1, c2, c3, c4, c5 = st.columns([1.1, 5, 2, 2, 2])
            with c1:
                st.checkbox("", key=f"chk_{b['id']}", value=False)
                # b["image"] pode ser URL ou caminho local (ex.: img/arquivo.jpg)
                st.image(b["image"], width=72)
            with c2:
                st.write(f"### {b['title']}")
                st.caption(f"{b['author']} • {b['genre']}")
                st.caption(f"Lançamento: {b['release_date']}")
                st.write(f"**{money(b['price'])}**")
                st.caption(f"⭐ {b['rating']} • {b['format']} • {b['language']}")
            with c3:
                st.caption("Estoque")
                st.write("✅ Disponível" if b.get("stock", 0) > 0 else "❌ Indisponível")
            with c4:
                st.caption("Entrega")
                st.write("Imediata" if b.get("format") == "Ebook" else "3-7 dias úteis")
            with c5:
                st.caption("")
                st.button("Adicionar", key=f"add_{b['id']}", on_click=add_to_cart, args=(b["id"], b["price"]))
        else:
            # Grade
            st.image(b["image"], use_column_width=True)
            st.write(f"**{b['title']}**")
            st.caption(f"{b['author']}")
            st.caption(f"⭐ {b['rating']} • {b['genre']}")
            st.write(money(b["price"]))
            st.button("Adicionar", key=f"add_grid_{b['id']}", on_click=add_to_cart, args=(b["id"], b["price"]))

def paginate(items: List[Dict], page: int, per_page: int = 6):
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total

# ---------- App ----------
init_state()
books = load_books()
books_map = {b["id"]: b for b in books}

# Header
left, right = st.columns([6, 2])
with left:
    st.title("📚 Loja de Livros")
    st.caption("E-commerce em Streamlit com lista/grade, filtros, carrinho e assistente de voz.")
with right:
    toggle_on = st.toggle(
        "Modo Grade",
        key="view_toggle",
        value=(st.session_state.view_mode == "Grade"),
        help="Alterna entre Lista e Grade",
    )
    st.session_state.view_mode = "Grade" if toggle_on else "Lista"

# === Assistente de Voz ===
st.divider()
voice_on = st.toggle("🎙️ Assistente de Voz (beta)", value=False, help="Ativa o agente de IA por voz")
if voice_on:
    components.html(
        """
        <iframe
            src="https://elevenlabs.io/app/talk-to?agent_id=agent_7801k2q24b9nfn7tcqpm6gfcep8v"
            style="width:100%; height:640px; border:0; border-radius:12px; overflow:hidden;"
            allow="microphone; autoplay; clipboard-write"
        ></iframe>
        """,
        height=660,
    )
# Botão flutuante (fallback se o iframe for bloqueado por CSP)
st.markdown(
    """
    <a href="https://elevenlabs.io/app/talk-to?agent_id=agent_7801k2q24b9nfn7tcqpm6gfcep8v"
       target="_blank"
       style="
         position: fixed;
         right: 24px;
         bottom: 24px;
         background: #6c5ce7;
         color: white;
         padding: 12px 16px;
         border-radius: 999px;
         text-decoration: none;
         font-weight: 600;
         box-shadow: 0 8px 24px rgba(0,0,0,.2);
         z-index: 9999;
       ">
       🎙️ Falar com a IA
    </a>
    """,
    unsafe_allow_html=True,
)

# Sidebar - Filtros e Carrinho
with st.sidebar:
    st.header("Filtros")
    q = st.text_input("Buscar por título, autor, gênero...", placeholder="Ex: Grisham, suspense, Gamache")
    genres = sorted({b["genre"] for b in books}) if books else []
    authors = sorted({b["author"] for b in books}) if books else []
    gsel = st.multiselect("Gênero", genres)
    asel = st.multiselect("Autor", authors)
    price_min, price_max = st.slider("Preço (R$)", 0.0, 300.0, (0.0, 300.0), step=10.0)
    order = st.selectbox("Ordenar por", ["Relevância", "Preço ↑", "Preço ↓", "Avaliação ↓", "Mais recentes"])
    st.divider()
    st.header("🛒 Carrinho")
    cart_summary(books_map)

# Filtragem
filtered = []
q_lower = (q or "").strip().lower()
for b in books:
    if q_lower and not (q_lower in b["title"].lower() or q_lower in b["author"].lower() or q_lower in b["genre"].lower()):
        continue
    if gsel and b["genre"] not in gsel:
        continue
    if asel and b["author"] not in asel:
        continue
    if not (price_min <= b["price"] <= price_max):
        continue
    filtered.append(b)

# Ordenação
if order == "Preço ↑":
    filtered.sort(key=lambda x: x["price"])
elif order == "Preço ↓":
    filtered.sort(key=lambda x: x["price"], reverse=True)
elif order == "Avaliação ↓":
    filtered.sort(key=lambda x: x["rating"], reverse=True)
elif order == "Mais recentes":
    def parse_date(d):
        try:
            return datetime.strptime(d, "%d/%m/%Y")
        except Exception:
            return datetime(1970, 1, 1)
    filtered.sort(key=lambda x: parse_date(x["release_date"]), reverse=True)

# Paginação
per_page = 8 if st.session_state.view_mode == "Grade" else 6
page_items, total = paginate(filtered, st.session_state.page, per_page)
pages = max(1, (total + per_page - 1) // per_page)

# Barra de resultado + paginação
c1, c2, c3 = st.columns([3, 4, 3])
with c1:
    st.write(f"**{total}** resultados")
with c2:
    pass
with c3:
    prev, pg, nxt = st.columns([1, 2, 1])
    with prev:
        if st.button("◀"):
            st.session_state.page = max(1, st.session_state.page - 1)
            st.rerun()
    with pg:
        st.number_input("Página", min_value=1, max_value=pages, step=1, key="page")
    with nxt:
        if st.button("▶"):
            st.session_state.page = min(pages, st.session_state.page + 1)
            st.rerun()

st.divider()

# Render
if st.session_state.view_mode == "Lista":
    for b in page_items:
        book_card(b, in_list=True)
else:
    # Grid 4 colunas
    cols = st.columns(4)
    for i, b in enumerate(page_items):
        with cols[i % 4]:
            book_card(b, in_list=False)

st.divider()
st.caption("Exemplo educacional • Streamlit • Sem backend de pagamento.")

# pages/checkout.py
import json
import pathlib
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Checkout", page_icon="🛒", layout="wide")



# ========= Helpers =========
@st.cache_data
def load_books() -> list[dict]:
    data_path = pathlib.Path("books.json")
    if not data_path.exists():
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def brl(value: float) -> str:
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def get_cart_items() -> dict:
    """
    Espera que st.session_state.cart seja:
    {
        "<book_id>": {"qty": int, "price": float, ...}
        # (em alguns apps, pode também conter title/author/genre)
    }
    """
    return st.session_state.get("cart", {})

def cart_totals(cart: dict) -> tuple[int, float]:
    total_itens = sum(int(item.get("qty", 1)) for item in cart.values())
    total_valor = sum(float(item.get("price", 0.0)) * int(item.get("qty", 1)) for item in cart.values())
    return total_itens, total_valor

def title_from_maps(book_id: str, cart_item: dict, books_map: dict) -> str:
    """Resolve o título do livro a partir do carrinho ou do books_map; cai no id se não achar."""
    # Se seu carrinho já tiver title (ou foi atualizado), use-o
    t = cart_item.get("title")
    if t:
        return str(t)
    # Caso contrário, busque no catálogo carregado
    b = books_map.get(book_id)
    if b and "title" in b:
        return str(b["title"])
    # Fallback final: mostra o id
    return f"Livro ({book_id})"

def author_from_maps(book_id: str, cart_item: dict, books_map: dict) -> str:
    a = cart_item.get("author")
    if a:
        return str(a)
    b = books_map.get(book_id)
    if b and "author" in b:
        return str(b["author"])
    return ""

def genre_from_maps(book_id: str, cart_item: dict, books_map: dict) -> str:
    g = cart_item.get("genre")
    if g:
        return str(g)
    b = books_map.get(book_id)
    if b and "genre" in b:
        return str(b["genre"])
    return ""

def cart_titles_markdown(cart: dict, books_map: dict) -> str:
    """Lista simples com nomes dos livros e quantidades."""
    if not cart:
        return "_—_"
    linhas = []
    for pid, item in cart.items():
        titulo = title_from_maps(pid, item, books_map)
        qty = int(item.get("qty", 1))
        linhas.append(f"- **{titulo}** _(x{qty})_")
    return "\n".join(linhas)

# ========= Página =========
st.markdown("### 🧾 Checkout")
st.caption("Revise seus itens e conclua sua compra.")

# Carrega catálogo para resolver nomes por id
books = load_books()
books_map = {b.get("id"): b for b in books if b.get("id")}

cart = get_cart_items()
if not cart:
    st.info("Seu carrinho está vazio.")
    col = st.columns([1, 1, 1])[1]
    with col:
        if st.button("Voltar para a loja", use_container_width=True):
            try:
                st.switch_page("app.py")
            except Exception:
                st.session_state.page = "Loja"
                st.rerun()
    st.stop()

# Cabeçalho com totais
total_itens, total_valor = cart_totals(cart)
top_l, top_r = st.columns([3, 1])
with top_l:
    st.markdown(f"**Itens no carrinho:** {total_itens}")
    st.markdown(f"**Atualizado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
with top_r:
    st.metric(label="Total", value=brl(total_valor))

st.divider()

# Lista explícita dos nomes dos livros
st.subheader("📚 Livros no carrinho")
st.markdown(cart_titles_markdown(cart, books_map))

st.divider()

# Lista detalhada (cards)
for pid, item in cart.items():
    title = title_from_maps(pid, item, books_map)
    author = author_from_maps(pid, item, books_map)
    genre = genre_from_maps(pid, item, books_map)
    price = float(item.get("price", 0.0))
    qty = int(item.get("qty", 1))
    subtotal = price * qty

    c1, c2, c3, c4 = st.columns([6, 2, 2, 2])
    with c1:
        st.markdown(f"**{title}**")
        sub = []
        if author: sub.append(author)
        if genre: sub.append(genre)
        st.caption(" • ".join(sub) if sub else "—")
    with c2:
        st.markdown("**Preço**")
        st.write(brl(price))
    with c3:
        st.markdown("**Qtd.**")
        st.write(qty)
    with c4:
        st.markdown("**Subtotal**")
        st.write(brl(subtotal))

    st.markdown("---")

# Resumo final e ações
sum_l, sum_r = st.columns([2, 1])
with sum_l:
    st.subheader("Resumo do pedido")
    st.write(f"**Itens:** {total_itens}")
    st.write(f"**Total:** {brl(total_valor)}")

with sum_r:
    st.subheader("Ações")
    confirm = st.button("Confirmar compra", type="primary", use_container_width=True)
    back = st.button("Voltar para a loja", use_container_width=True)
    if confirm:
        st.success("Pedido confirmado! Obrigado pela compra. 🎉")
        st.session_state.cart = {}
    elif back:
        try:
            st.switch_page("app.py")
        except Exception:
            st.session_state.page = "Loja"
            st.rerun()

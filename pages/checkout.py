import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Checkout", page_icon="🛒", layout="wide")

# ---------- Helpers ----------
def brl(value: float) -> str:
    # Formata em R$ sem depender de locale do SO
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def get_cart_items():
    """
    Espera que st.session_state.cart seja um dict assim:
    {
        "id_do_livro": {
            "title": "Título",
            "author": "Autor",
            "price": 49.9,
            "qty": 1,
            "genre": "Suspense",
            "thumb": "URL opcional da capa"
        },
        ...
    }
    """
    return st.session_state.get("cart", {})

def cart_totals(cart: dict):
    total_itens = sum(item.get("qty", 1) for item in cart.values())
    total_valor = sum(item.get("price", 0.0) * item.get("qty", 1) for item in cart.values())
    return total_itens, total_valor

# ---------- Página ----------
st.markdown("### 🧾 Checkout")
st.caption("Revise seus itens e conclua sua compra.")

cart = get_cart_items()
if not cart:
    st.info("Seu carrinho está vazio.")
    col = st.columns([1, 1, 1])[1]
    with col:
        if st.button("Voltar para a loja", use_container_width=True):
            # Volta para a página principal
            try:
                st.switch_page("app.py")
            except Exception:
                st.session_state.page = "Loja"
                st.rerun()
    st.stop()

# Cabeçalho com totals
total_itens, total_valor = cart_totals(cart)
top_l, top_r = st.columns([3, 1])
with top_l:
    st.markdown(f"**Itens no carrinho:** {total_itens}")
    st.markdown(f"**Atualizado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
with top_r:
    st.metric(label="Total", value=brl(total_valor))

st.divider()

# Lista de itens (estilo “cards” simples)
for pid, item in cart.items():
    title = item.get("title", "Livro")
    author = item.get("author", "")
    genre = item.get("genre", "")
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

# Resumo final
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
        # Aqui você pode integrar seu provedor de pagamento
        st.success("Pedido confirmado! Obrigado pela compra. 🎉")
        # Opcional: limpar carrinho
        st.session_state.cart = {}
    elif back:
        try:
            st.switch_page("app.py")
        except Exception:
            st.session_state.page = "Loja"
            st.rerun()

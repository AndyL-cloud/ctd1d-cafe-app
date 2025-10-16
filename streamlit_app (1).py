import streamlit as st
from typing import Dict, Tuple

# -------------------- App config --------------------
st.set_page_config(page_title="CTD1D Café", page_icon="☕", layout="centered")

# -------------------- Data --------------------------
MENU: Dict[str, float] = {
    # Coffee
    "Mocha": 15.00,
    "Latte": 17.00,
    "Cappuccino": 16.50,
    # Tea / Other
    "Tea": 1.50,
    # Juices
    "Apple Juice": 2.00,
    "Lemon Juice": 2.25,
    # Cakes (so combo Coffee+Cake works)
    "Cheesecake": 8.00,
    "Chocolate Cake": 7.50,
}

CATEGORY: Dict[str, str] = {
    "Mocha": "coffee",
    "Latte": "coffee",
    "Cappuccino": "coffee",
    "Tea": "other",
    "Apple Juice": "juice",
    "Lemon Juice": "juice",
    "Cheesecake": "cake",
    "Chocolate Cake": "cake",
}

SLOTS = ["09:00–11:59", "12:00–14:59", "15:00–17:59", "18:00–20:59"]

def slot_to_band(s: str) -> str:
    """Map slot → pricing band."""
    idx = SLOTS.index(s)
    if idx == 0:          # 09:00–11:59
        return "morning"
    if idx in (1, 2):     # 12:00–17:59
        return "afternoon"
    return "evening"      # 18:00–20:59

def has_combo(order_dict: Dict[str, int]) -> bool:
    """True if at least one coffee AND one cake are ordered."""
    has_coffee = any(CATEGORY.get(i) == "coffee" and q > 0 for i, q in order_dict.items())
    has_cake   = any(CATEGORY.get(i) == "cake"   and q > 0 for i, q in order_dict.items())
    return has_coffee and has_cake

def line_total_with_discounts(item: str, qty: int, band: str, combo_active: bool) -> Tuple[float, float, float]:
    """
    Calculate per-line pricing.
    Returns (line_before_time, time_discount_amount, line_after_time).
    - Bulk rule example: qty ≥ 3 → 10% off BEFORE time discount
    - Time rules:
        * evening: 30% off everything
        * afternoon: 20% off juice
        * morning: 20% off coffee+cake if combo present
    """
    unit = MENU[item]
    line = unit * qty
    if qty >= 3:
        line *= 0.90

    cat = CATEGORY.get(item, "other")
    pct = 0.0
    if band == "evening":
        pct = 0.30
    elif band == "afternoon" and cat == "juice":
        pct = 0.20
    elif band == "morning" and combo_active and cat in {"coffee", "cake"}:
        pct = 0.20

    disc = round(line * pct, 2)
    after = round(line - disc, 2)
    return round(line, 2), disc, after

# -------------------- Session state -----------------
if "page" not in st.session_state:
    st.session_state.page = "order"   # "order" or "bill"
if "order" not in st.session_state:
    st.session_state.order = {k: 0 for k in MENU.keys()}
if "slot" not in st.session_state:
    st.session_state.slot = SLOTS[0]

# -------------------- Header ------------------------
st.title("☕ CTD1D Café — Team Streamlit App")

# -------------------- Page: Order -------------------
if st.session_state.page == "order":
    st.subheader("1) Choose time of day (shop hours 9am–9pm)")
    st.session_state.slot = st.radio("Time slot", SLOTS, index=SLOTS.index(st.session_state.slot), horizontal=True)
    band = slot_to_band(st.session_state.slot)
    st.caption(
        f"Active band: **{band}**  • Rules — "
        "Morning: 20% off Coffee+Cake (combo) • "
        "Afternoon: 20% off Fruit Juice • "
        "Evening: 30% off everything • "
        "Bulk: buy ≥3 of same item → 10% off before time discount"
    )

    st.subheader("2) Add quantities")
    with st.form("order_form", clear_on_submit=False):
        cols = st.columns(2)
        new_order = {}
        for i, item in enumerate(MENU.keys()):
            with cols[i % 2]:
                new_order[item] = st.number_input(
                    f"{item} — ${MENU[item]:.2f}",
                    min_value=0, step=1, value=st.session_state.order.get(item, 0),
                    key=f"qty_{item}"
                )
        c1, c2, c3 = st.columns([1,1,2])
        submitted = c1.form_submit_button("Review bill ➜", use_container_width=True)
        reset = c2.form_submit_button("Reset", use_container_width=True)

    if reset:
        st.session_state.order = {k: 0 for k in MENU.keys()}
        st.rerun()

    if submitted:
        st.session_state.order = new_order
        st.session_state.page = "bill"
        st.rerun()

# -------------------- Page: Bill --------------------
if st.session_state.page == "bill":
    st.subheader("Your bill")
    band = slot_to_band(st.session_state.slot)
    order = {k: v for k, v in st.session_state.order.items() if v > 0}

    if not order:
        st.info("Your cart is empty. Add some items first.")
    else:
        combo_active = has_combo(order)

        # Build table
        rows = []
        subtotal_before_time = 0.0
        total_time_disc = 0.0
        grand_total = 0.0

        for item, qty in order.items():
            before, tdisc, after = line_total_with_discounts(item, qty, band, combo_active)
            rows.append({
                "Item": item,
                "Qty": qty,
                "Unit ($)": f"{MENU[item]:.2f}",
                "Line before time ($)": f"{before:.2f}",
                "Time discount ($)": f"-{tdisc:.2f}" if tdisc else "0.00",
                "Line after time ($)": f"{after:.2f}",
            })
            subtotal_before_time += before
            total_time_disc += tdisc
            grand_total += after

        st.table(rows)
        st.write("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Subtotal (before time)", f"${subtotal_before_time:.2f}")
        c2.metric("Time discounts", f"-${total_time_disc:.2f}")
        c3.metric("Grand total", f"${grand_total:.2f}")

        if combo_active and band == "morning":
            st.caption("✅ Morning combo active: Coffee & Cake items received 20% off.")

    # Navigation
    b1, b2 = st.columns([1,1])
    if b1.button("⬅ Back to order", use_container_width=True):
        st.session_state.page = "order"
        st.rerun()
    if b2.button("✅ Confirm order", use_container_width=True):
        st.success("Order confirmed! (You can hook this up to your backend or a Google Sheet.)")

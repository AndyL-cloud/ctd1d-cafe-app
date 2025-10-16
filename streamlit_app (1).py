# cafe_app.py  —  simple 2-page Streamlit app

import streamlit as st

# ---------------- Basic setup ----------------
st.set_page_config(page_title="CTD1D Café", page_icon="☕")

# Menu & categories (edit these freely)
MENU = {
    "Mocha": 15.00,
    "Latte": 17.00,
    "Cappuccino": 16.50,
    "Tea": 1.50,
    "Apple Juice": 2.00,
    "Lemon Juice": 2.25,
    "Cheesecake": 8.00,
    "Chocolate Cake": 7.50,
}
CATEGORY = {
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


# --------------- Helper functions ---------------
def slot_to_band(s):
    """Map time slot text to pricing band."""
    i = SLOTS.index(s)
    if i == 0:
        return "morning"
    if i in (1, 2):
        return "afternoon"
    return "evening"

def has_combo(order_dict):
    """True when there's at least one coffee and one cake."""
    has_coffee = any(CATEGORY.get(it) == "coffee" and q > 0 for it, q in order_dict.items())
    has_cake   = any(CATEGORY.get(it) == "cake"   and q > 0 for it, q in order_dict.items())
    return has_coffee and has_cake

def line_total_with_discounts(item, qty, band, combo_active):
    """
    Returns: (line_before_time, time_discount_amount, final_line_total)
    Rules:
      - Bulk: qty >= 3  → 10% off BEFORE time-based discount
      - Evening: 30% off everything
      - Afternoon: 20% off juices
      - Morning: 20% off coffee + cake IF there's a combo (both ordered)
    """
    unit = MENU[item]
    line = unit * qty
    # bulk discount first
    if qty >= 3:
        line *= 0.90

    cat = CATEGORY.get(item, "other")
    pct = 0.0
    if band == "evening":
        pct = 0.30
    elif band == "afternoon" and cat == "juice":
        pct = 0.20
    elif band == "morning" and combo_active and cat in ("coffee", "cake"):
        pct = 0.20

    time_disc = round(line * pct, 2)
    after = round(line - time_disc, 2)
    return round(line, 2), time_disc, after


# --------------- Session state (simple) ---------------
if "page" not in st.session_state:
    st.session_state.page = "order"   # "order" or "bill"
if "order" not in st.session_state:
    st.session_state.order = {k: 0 for k in MENU}
if "slot" not in st.session_state:
    st.session_state.slot = SLOTS[0]


# --------------- UI ---------------
st.title("☕ CTD1D Café")

if st.session_state.page == "order":
    st.subheader("1) Choose time of day")
    st.session_state.slot = st.radio(
        "Time slot",
        SLOTS,
        index=SLOTS.index(st.session_state.slot),
        horizontal=True,
    )
    band = slot_to_band(st.session_state.slot)
    st.caption(
        f"Active band: **{band}**  |  Morning: 20% off Coffee+Cake (combo) • "
        f"Afternoon: 20% off Juices • Evening: 30% off everything • "
        f"Bulk: ≥3 of same item → 10% off (applied before time discount)"
    )

    st.subheader("2) Add quantities")
    cols = st.columns(2)
    new_order = {}
    for i, item in enumerate(MENU):
        with cols[i % 2]:
            new_order[item] = st.number_input(
                f"{item} — ${MENU[item]:.2f}",
                min_value=0,
                step=1,
                value=st.session_state.order.get(item, 0),
                key=f"qty_{item}",
            )

    c1, c2 = st.columns(2)
    if c1.button("Review bill ➜", use_container_width=True):
        st.session_state.order = new_order
        st.session_state.page = "bill"
        st.rerun()
    if c2.button("Reset", use_container_width=True):
        st.session_state.order = {k: 0 for k in MENU}
        st.rerun()

# -------------------- BILL PAGE --------------------
if st.session_state.page == "bill":
    st.subheader("Your bill")
    band = slot_to_band(st.session_state.slot)
    order = {k: v for k, v in st.session_state.order.items() if v > 0}

    if not order:
        st.info("Your cart is empty. Go back and add some items.")
    else:
        combo_active = has_combo(order)

        rows = []
        subtotal_before = 0.0
        total_time_disc = 0.0
        grand_total = 0.0

        for item, qty in order.items():
            before, disc, after = line_total_with_discounts(item, qty, band, combo_active)
            rows.append(
                {
                    "Item": item,
                    "Qty": qty,
                    "Unit ($)": f"{MENU[item]:.2f}",
                    "Line before time ($)": f"{before:.2f}",
                    "Time discount ($)": f"-{disc:.2f}" if disc else "0.00",
                    "Line after time ($)": f"{after:.2f}",
                }
            )
            subtotal_before += before
            total_time_disc += disc
            grand_total += after

        st.table(rows)
        st.write("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Subtotal (before time)", f"${subtotal_before:.2f}")
        c2.metric("Time discounts", f"-${total_time_disc:.2f}")
        c3.metric("Grand total", f"${grand_total:.2f}")

        if combo_active and band == "morning":
            st.caption("✅ Morning combo active: Coffee & Cake items received 20% off.")

    b1, b2 = st.columns(2)
    if b1.button("⬅ Back to order", use_container_width=True):
        st.session_state.page = "order"
        st.rerun()
    if b2.button("✅ Confirm order", use_container_width=True):
        st.success("Order confirmed! (Hook this up to a sheet or database if needed.)")

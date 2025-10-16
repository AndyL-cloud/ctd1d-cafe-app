import streamlit as st

st.title("☕️ Café Corner — with Time Toggle Discounts")

# ---------- Menu (keep your existing items here) ----------
menu = {
    "Espresso": 2.50,
    "Latte": 3.50,
    "Cappuccino": 3.00,
    "Tea": 2.00,
    "Croissant": 2.75,
    "Muffin": 2.25,
    # Uncomment if you want the afternoon rule to apply:
    # "Fruit Juice": 2.80,
}

# Map items to simple categories for rules
CATEGORY = {
    "Espresso": "coffee", "Latte": "coffee", "Cappuccino": "coffee",
    "Croissant": "cake", "Muffin": "cake",
    "Tea": "other", "Fruit Juice": "juice"
}

st.header("Menu")
order = {}
for item, price in menu.items():
    qty = st.number_input(
        label=f"{item} (${price:.2f})",
        min_value=0, max_value=10, value=0, step=1, key=item
    )
    if qty:
        order[item] = qty

st.divider()

# ---------- (1) Time-of-day toggle every 3 hours ----------
st.subheader("⏰ Choose time of day")
SLOTS = [
    "00:00–02:59", "03:00–05:59", "06:00–08:59",
    "09:00–11:59", "12:00–14:59", "15:00–17:59",
    "18:00–20:59", "21:00–23:59"
]
slot = st.radio("Time slot", SLOTS, horizontal=True)

def slot_to_band(s: str) -> str:
    """Map a 3-hour slot to a discount band."""
    idx = SLOTS.index(s)
    # 0: 00–02, 1: 03–05, 2: 06–08, 3: 09–11, 4: 12–14, 5: 15–17, 6: 18–20, 7: 21–23
    if idx in (2, 3):       # 06–11
        return "morning"
    if idx in (4, 5):       # 12–17
        return "afternoon"
    return "night"          # 18–05 (night covers 18–23 and 00–05)

band = slot_to_band(slot)
st.caption(f"Active band: **{band}**")

# ---------- (2) Discount engine ----------
def has_combo(order_dict) -> bool:
    has_coffee = any(CATEGORY.get(i) == "coffee" for i, q in order_dict.items() if q > 0)
    has_cake   = any(CATEGORY.get(i) == "cake"   for i, q in order_dict.items() if q > 0)
    return has_coffee and has_cake

def line_total_with_discounts(item: str, qty: int, band: str, combo_active: bool) -> tuple[float, float, float]:
    """Return (line_subtotal_before_time_discount, time_discount_amount, final_line_total)."""
    unit = menu[item]
    # Optional bulk rule: ≥3 of same item → 10% off BEFORE time-based discount
    line = unit * qty
    if qty >= 3:
        line *= 0.90  # bulk 10%

    cat = CATEGORY.get(item, "other")
    pct = 0.0
    if band == "night":
        pct = 0.30
    elif band == "afternoon" and cat == "juice":
        pct = 0.20
    elif band == "morning" and combo_active and cat in {"coffee", "cake"}:
        pct = 0.20

    d = round(line * pct, 2)
    after = round(line - d, 2)
    return round(line, 2), d, after

# ---------- (3) Summary / receipt like your test.py ----------
if order:
    st.header("Your Order (with discounts)")
    combo = has_combo(order)
    subtotal = 0.0
    discount_sum = 0.0
    grand_total = 0.0

    for item, qty in order.items():
        line_before, disc, line_after = line_total_with_discounts(item, qty, band, combo)
        subtotal += line_before
        discount_sum += disc
        grand_total += line_after
        st.write(f"{item} × {qty} — Subtotal ${line_before:.2f} | Discount -${disc:.2f} | Line Total ${line_after:.2f}")

    st.markdown(f"**Subtotal:** ${subtotal:.2f}  \n**Total Discount:** -${discount_sum:.2f}  \n**Grand Total:** **${grand_total:.2f}**")

    if st.button("Place Order"):
        st.success("🎉 Your order has been placed!")
        st.balloons()
else:
    st.info("Select at least one item to see your order summary.")

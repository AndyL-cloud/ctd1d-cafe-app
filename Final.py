import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Cafe App", layout="wide")

# --- Persist quantities in session_state ---
prod1 = 0
prod2 = 0
prod3 = 0

# --- Navigation ---
page = st.sidebar.radio("Go to", ["Menu", "Cart & Checkout"])

## Haziq's product definitions -------------------------
coffee  = {"Name": "Coffee",      "Price": 3}
frjuice = {"Name": "Fruit Juice", "Price": 2}
cake    = {"Name": "Cake",        "Price": 6}
menu    = [coffee, frjuice, cake]

def find_price(item_name):
    for prod in menu:
        if prod["Name"] == item_name:
            return prod["Price"]

## Common time‐discount logic ----------------------------
SLOTS = ["09:00–11:59","12:00–14:59","15:00–17:59","18:00–20:59"]
def slot_to_band(s):
    if s=="09:00–11:59": return "morning"
    if s in ("12:00–14:59","15:00–17:59"): return "afternoon"
    return "evening"

# Choose time‐slot (always shown in sidebar so both pages know the band)
slot = st.sidebar.radio("Time slot", SLOTS, index=0)
band = slot_to_band(slot)

# Utility to detect the morning combo
def has_combo(order):
    return order["Coffee"]>=1 and order["Cake"]>=1

# Fill an order dict from session_state
order_now = {
    "Coffee":      st.session_state.prod1,
    "Fruit Juice": st.session_state.prod2,
    "Cake":        st.session_state.prod3
}

# --- PAGE 1: MENU ---
if page == "Menu":
    st.title("☕ Welcome to our Cafe!")
    st.write("Select quantities below and they will carry over to your cart.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://cdn.shopify.com/s/files/1/0669/0966/7619/files/espresso-shot-crema-in-white-cup-on-wood-table-wrexham-bean.webp?v=1745257519")
        st.number_input("Coffee  ($3 each)",      min_value=0, max_value=10, step=1, key="prod1")
    with col2:
        st.image("https://emilylaurae.com/wp-content/uploads/2022/08/passion-fruit-juice-2.jpg")
        st.number_input("Fruit Juice  ($2 each)", min_value=0, max_value=10, step=1, key="prod2")
    with col3:
        st.image("https://static.vecteezy.com/system/resources/previews/001/738/638/large_2x/chocolate-cake-slice-free-photo.jpg")
        st.number_input("Cake Slice  ($6 each)",  min_value=0, max_value=10, step=1, key="prod3")
    
    st.markdown("---")
    st.write("When you’re ready to see your cart and checkout, switch to **Cart & Checkout** in the sidebar.")

# --- PAGE 2: CART & CHECKOUT ---
else:
    st.title("🛒 Cart & Checkout")
    st.subheader(f"Time Slot: **{slot}**  →  Band: **{band}**")
    st.caption(
        "• Morning: 20% off Coffee+Cake combo  \n"
        "• Afternoon: 20% off Fruit Juice     \n"
        "• Evening: 30% off everything        \n"
        "• Bulk (≥3 of same): extra 10% off "
    )

    # build table rows
    rows = []
    total_raw, total_bulk, total_time, grand_total = 0,0,0,0

    morning_combo = has_combo(order_now)

    for item, qty in order_now.items():
        if qty <= 0:
            continue
        unit_price = find_price(item)
        raw = unit_price * qty
        # bulk discount
        before_time = raw * (0.9 if qty >= 3 else 1.0)
        bulk_disc = raw - before_time

        # time‐band discount factor
        if band == "evening":
            tdf = 0.30
        elif band == "afternoon" and item=="Fruit Juice":
            tdf = 0.20
        elif band == "morning" and morning_combo and item in ("Coffee","Cake"):
            tdf = 0.20
        else:
            tdf = 0.0

        time_disc = before_time * tdf
        after_time = before_time - time_disc

        rows.append({
            "Item": item,
            "Qty": qty,
            "Unit ($)": unit_price,
            "Raw ($)": raw,
            "Bulk Disc ($)": round(bulk_disc,2),
            "Before Time Disc ($)": round(before_time,2),
            "Time Disc ($)": round(time_disc,2),
            "Total ($)": round(after_time,2)
        })

        total_raw     += raw
        total_bulk    += bulk_disc
        total_time    += time_disc
        grand_total   += after_time

    if not rows:
        st.info("Your cart is empty. Go back to **Menu** and add something!")
    else:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        st.markdown(
            f"**Raw total:** ${total_raw:.2f}  \n"
            f"**Bulk discounts:** −${total_bulk:.2f}  \n"
            f"**Time-band discounts:** −${total_time:.2f}  \n"
            f"### **Grand total: ${grand_total:.2f}**"
        )

        if st.button("✅ CHECKOUT"):
            st.success(f"Checked out! Your final bill is ${grand_total:.2f}. Thank you!")
            # (you could also reset session_state here if you like)
            # st.session_state.prod1 = st.session_state.prod2 = st.session_state.prod3 = 0

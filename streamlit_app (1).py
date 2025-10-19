import streamlit as st
import pandas as pd
import time

## LIST OF PRODUCTS ------------------------------------------------------------------------
coffee = {'Name' : 'Coffee', 'Price' : 3,'Type' : ['Mocha', 'Latte', 'Cappuccino']}
frjuice = {'Name' : 'Fruit Juice', 'Price' : 2, 'Type' : ['Apple', 'Lemon', 'Watermelon']}
cake = {'Name' : 'Cake', 'Price' : 6, 'Type' : ['Chocolate', 'Vanilla', 'Cheese']}
## -----------------------------------------------------------------------------------------

## INITIALISE VARIABLES --------------------------------------------------------------------
prod1 = 0
prod2 = 0
prod3 = 0
## -----------------------------------------------------------------------------------------

## SHOW PRODUCTS AS MENU -------------------------------------------------------------------
st.title('Welcome to our Cafe interface! :coffee:')
st.write('Please select your order:')

## Seperating one line into the columns
col1, col2, col3 = st.columns(3)

## Assigning to different columns
with col1:
  st.image('https://cdn.shopify.com/s/files/1/0669/0966/7619/files/espresso-shot-crema-in-white-cup-on-wood-table-wrexham-bean.webp?v=1745257519')
  st.number_input("Coffee  >>>  $3.00 each", min_value=0, max_value=10, step=1, key="prod1")

with col2:
  st.image('https://farmtojar.com/wp-content/uploads/2016/11/5BA949BB-3B24-4216-B700-E5FE2AF12F7F.jpeg')
  st.number_input("Fruit Juice  >>>  $2.00 each", min_value=0, max_value=10, step=1, key="prod2")

with col3:
  st.image('https://www.livingnorth.com/images/media/articles/food-and-drink/eat-and-drink/coffee.png?')
  st.number_input("Cake Slice  >>>  $6.00 each", min_value=0, max_value=10, step=1, key="prod3")
## ------------------TIME SLOT-----------------
SLOTS = ["09:00–11:59", "12:00–14:59", "15:00–17:59", "18:00–20:59"]

def slot_to_band(s: str) -> str:
    if s == "09:00–11:59":
        return "morning"
    elif s in ("12:00–14:59", "15:00–17:59"):
        return "afternoon"
    else:
        return "evening"
st.subheader("⏰ Choose time of day")
slot = st.radio("Time slot", SLOTS, index=0, horizontal=True)
band = slot_to_band(slot)
st.caption(
    f"Active band: **{band}**  • "
    "Morning: 20% off Coffee+Cake (combo) • "
    "Afternoon: 20% off Fruit Juice • "
    "Evening: 30% off everything • "
    "Bulk: ≥3 same item = extra 10% off (before time discount)"
)

'''
## START CALCULATING WHEN BUTTON PRESSED ---------------------------------------------------
if st.button('CHECKOUT'):

  ## Calculations using user inputs
  prod1 = int(st.session_state.prod1)
  price1 = coffee['Price'] * prod1

  prod2 = int(st.session_state.prod2)
  price2 = frjuice['Price'] * prod2

  prod3 = int(st.session_state.prod3)
  price3 = cake['Price'] * prod3

  total = price1 + price2 + price3
'''
## ---------------------------discount engine setup-Andy--------------------------------------------------
MENU = {
    "Coffee": coffee["Price"],
    "Fruit Juice": frjuice["Price"],
    "Cake": cake["Price"],
}
CATEGORY = {"Coffee": "coffee", "Fruit Juice": "juice", "Cake": "cake"}

def has_combo(order_dict) -> bool:
    has_coffee = any(CATEGORY[i] == "coffee" for i, q in order_dict.items() if q > 0)
    has_cake   = any(CATEGORY[i] == "cake"   for i, q in order_dict.items() if q > 0)
    return has_coffee and has_cake

def line_total_with_discounts(item: str, qty: int, band: str, combo: bool):
    """
    Returns (line_before_time, time_discount_amount, line_after_time)
      - Bulk: qty >= 3 → 10% off BEFORE time-based discount
      - Evening: 30% off everything
      - Afternoon: 20% off juices
      - Morning: 20% off coffee + cake IF combo active
    """
    unit = MENU[item]
    line = unit * qty
    if qty >= 3:
        line *= 0.90  # bulk first

    pct = 0.0
    cat = CATEGORY[item]
    if band == "evening":
        pct = 0.30
    elif band == "afternoon" and cat == "juice":
        pct = 0.20
    elif band == "morning" and combo and cat in {"coffee", "cake"}:
        pct = 0.20

    time_disc = round(line * pct, 2)
    after = round(line - time_disc, 2)
    return round(line, 2), time_disc, after

## DISPLAYING RECEIPT AS A TABLE (KHANSKY) -------------------------------------------------
menu = [coffee, frjuice, cake]

#just for the prices individually bruh
def find_price(item_name):
    for category in menu:
        if item_name in category['Name']:
            return category['Price']

#actual main command that you use to pull
def receipt(full_list):
    #creates new list that willo be used to combine allat
    idlist = []
    quantitylist = []
    pricelist = []
    subtotal = []

    #seperates the full_list into 4 seperate columns: id, qty, price, sub
    for individual_items, individual_qty in full_list:
        price = find_price(individual_items)
        idlist.append(individual_items)
        quantitylist.append(individual_qty)
        pricelist.append(price)
        subtotal.append(individual_qty*price)

    #panda that into something pandable
    fullframe = pd.DataFrame({'Item':idlist, 'Quantity':quantitylist, 'Price per Item($)':pricelist, 'Subtotal($)':subtotal})

    #return allat work
    return fullframe


full_list = [(coffee['Name'], prod1), (frjuice['Name'], prod2), (cake['Name'], prod3)]
st.write(receipt(full_list))
## -----------------------------------------------------------------------------------------


## ORIGINAL CODE BELOW ---------------------------------------------------------------------
'''
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
'''

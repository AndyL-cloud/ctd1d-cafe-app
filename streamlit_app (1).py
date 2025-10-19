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

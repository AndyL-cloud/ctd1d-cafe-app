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
st.title('Welcome to our Cafe interface!')
st.write('Please select your order:')

## Seperating one line into the columns
col1, col2, col3 = st.columns(3)

## Assigning to different columns
with col1:
  st.image('https://cdn.shopify.com/s/files/1/0669/0966/7619/files/espresso-shot-crema-in-white-cup-on-wood-table-wrexham-bean.webp?v=1745257519')
  st.number_input("Coffee  >>>  $3.00 each", min_value=0, max_value=10, step=1, key="prod1")

with col2:
  st.image('https://emilylaurae.com/wp-content/uploads/2022/08/passion-fruit-juice-2.jpg')
  st.number_input("Fruit Juice  >>>  $2.00 each", min_value=0, max_value=10, step=1, key="prod2")

with col3:
  st.image('https://static.vecteezy.com/system/resources/previews/001/738/638/large_2x/chocolate-cake-slice-free-photo.jpg')
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
st.subheader("Choose time of day")
slot = st.radio("Time slot", SLOTS, index=0, horizontal=True)
band = slot_to_band(slot)
st.caption(
    f""""Active band: **{band}**  •
    Morning: 20% off Coffee+Cake (combo) •
    Afternoon: 20% off Fruit Juice •
    Evening: 30% off everything •
    Bulk: ≥3 same item = extra 10% off (before time discount)"""
)

## -----------------------------------------------------------------------------------------

## ANDY & WAI YAN'S BLOCK--------------------------------------------------------------------------
## Morning combo discount function --------------------------------------------------------------------
def has_combo(order_now):
    if order_now["Coffee"] >= 1 and order_now["Cake"] >= 1:
        return True
    else:
        return False

## Getting user input and assigning zero as default value if there is no input --------------------------------------------------------------------
prod1 = int(st.session_state.get("prod1",0))
prod2 = int(st.session_state.get("prod2",0))
prod3 = int(st.session_state.get("prod3",0))

## Assinging user's order into a dictionary --------------------------------------------------------------------
order_now = {"Coffee": prod1, "Fruit Juice":prod2, "Cake":prod3}

morning = has_combo(order_now)

menu = [coffee, frjuice, cake]

## Getting price of items function by Khansky--------------------------------------------------------------------
def find_price(item_name):
    for category in menu:
        if(item_name == category['Name']):
            return category['Price']

## Displaying items, their prices, and discounts of items in the cart--------------------------------------------------------------------
st.subheader("🛒 Your cart (with discounts)")

rows = []
total_raw = 0.0
total_bulk_disc = 0.0
total_time_disc = 0.0
grand_total = 0.0

## Looping to calculate the total price, including time and bulk discounts --------------------------------------------------------------------
for item, qty in order_now.items():
    if qty <=0:
        continue
    unit = find_price(item)
    raw = round(unit*qty,2)

    before_time_disc = raw
    if (qty >=3):
        before_time_disc = round(raw*0.9,2)
        
    time_disc_fac = 0.0
    if (band == "evening"):
        time_disc_fac = 0.3
    elif (band == "afternoon" and item == "Fruit Juice"):
        time_disc_fac = 0.2
    elif (band == "morning" and morning and item in {"Coffee", "Cake"}):
        time_disc_fac = 0.2

    time_disc = round(before_time_disc * time_disc_fac, 2)
    after_time_disc = round(before_time_disc - time_disc, 2)

    bulk_disc = round(raw - before_time_disc, 2)

    ## To show a total breakdown of the discounts in a table later on --------------------------------------------------------------------
    rows.append({
        "Item": item,
        "Qty": qty,
        "Unit ($)": unit,
        "Raw ($)": raw,
        "Bulk - ($)": bulk_disc,
        "Before time discount($)": before_time_disc,
        "Time disc - ($)": time_disc,
        "After time discount ($)": after_time_disc
    })
    
    total_raw += raw
    total_bulk_disc += bulk_disc
    total_time_disc += time_disc
    grand_total += after_time_disc

## This is the breakdown table --------------------------------------------------------------------
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.markdown(
        f"""
**Raw total:** ${total_raw:.2f}\n 
**Bulk discounts:** −${total_bulk_disc:.2f}\n
**Time-band discounts:** −${total_time_disc:.2f}  
### **Cart total now: ${grand_total:.2f}**
"""
    )
else:
    st.info("Your cart is empty. Add some items from the menu above!")

st.divider()

## DISPLAYING RECEIPT AS A TABLE (KHANSKY) -------------------------------------------------

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

## Adding a checkout button, displaying the full receipt and price breakdown at the bottom of the page --------------------------------------------------------------------
if st.button("CHECKOUT"):
    full_list = [(coffee['Name'], prod1), (frjuice['Name'], prod2), (cake['Name'], prod3)]
    st.subheader("🧾 Final receipt (items & subtotals)")
    st.write(receipt(full_list))

    # also show the same discount totals snapshot at checkout
    st.subheader("💸 Discount breakdown at checkout")
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.markdown(
            f"""
**Raw total:** ${total_raw:.2f}  
**Bulk discounts:** −${total_bulk_disc:.2f}  
**Time-band discounts:** −${total_time_disc:.2f}  
## **Amount due: ${grand_total:.2f}**
"""
        )
    else:
        st.info("No items were selected at checkout.")

import streamlit as st

"""
This Streamlit app presents a simple café ordering interface.  Customers can browse
the available items, select a product, choose a variant and a time slot for pickup,
and receive an automatic discount based on the chosen time slot.  The discount
values and time slots are defined in the `time_slots` dictionary below, making
them easy to modify without touching other parts of the app.

The app uses `st.session_state` to keep track of which page the user is on and
which product they selected.  This avoids relying on global mutable variables
and ensures that state persists across reruns.
"""

# Initialise session state for navigation and selection
if "page" not in st.session_state:
    st.session_state.page = 1
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

###############################################################################
# Item definitions
###############################################################################

## hzq code
## ----------------------------------------------------------------------------------------------------------------------------------------

coffee = {
    "Name": "Coffee",
    "Image": "https://images.pexels.com/photos/312418/pexels-photo-312418.jpeg?cs=srgb&dl=pexels-chevanon-312418.jpg&fm=jpg",
    "Price": 3,
    "Type": ["Mocha", "Latte", "Cappuccino"],
}

frjuice = {
    "Name": "Fruit Juice",
    "Image": "https://media.istockphoto.com/id/915657126/photo/orange-juice-glass-jar-shot-on-rustic-wooden-table.jpg?s=612x612&w=0&k=20&c=rlj0FwRDQOAV_j8-MUQntzIj8fZegbMewj22nNXxiYc=",
    "Price": 2,
    "Type": ["Apple", "Lemon", "Watermelon"],
}

cake = {
    "Name": "Cake",
    "Image": "https://static.vecteezy.com/system/resources/previews/001/738/638/large_2x/chocolate-cake-slice-free-photo.jpg",
    "Price": 6,
    "Type": ["Chocolate", "Vanilla", "Cheese"],
}

###############################################################################
# Time slots and discounts
###############################################################################
# Define the available time slots and the corresponding discount rates.
#
# The keys are human‑readable time ranges and the values are the fractional
# discounts (e.g., 0.10 means 10% off).  Adjust these values to change the
# discount policy.  Additional time ranges can be added as needed.
time_slots = {
    "09:00 – 12:00": 0.10,
    "12:00 – 15:00": 0.05,
    "15:00 – 18:00": 0.15,
    "18:00 – 21:00": 0.00,
}
##-----------------------------------------------------------------------------------------------------------------------------------------test

## ----------------------------------------------------------------------------------------------------------------------------------------

if st.session_state.page == 1:
    # Configure the page
    st.set_page_config(page_title="CTD1D Café", page_icon="☕", layout="centered")

    st.title("☕ CTD1D Café — Team Streamlit App")

    st.write("Welcome! What would you like to order?")

    # Display product cards
    col1, col2, col3 = st.columns(3)
    # Coffee card
    with col1:
        st.image(coffee["Image"], use_container_width=True)
        if st.button("Coffee", use_container_width=True):
            st.session_state.selected_product = coffee
            st.session_state.page = 2
    # Fruit Juice card
    with col2:
        st.image(frjuice["Image"], use_container_width=True)
        if st.button("Fruit Juice", use_container_width=True):
            st.session_state.selected_product = frjuice
            st.session_state.page = 2
    # Cake card
    with col3:
        st.image(cake["Image"], use_container_width=True)
        if st.button("Cake", use_container_width=True):
            st.session_state.selected_product = cake
            st.session_state.page = 2

    # Simple search demonstration (deduplicated)
    st.markdown("### Search demo")
    query = st.text_input("Search", placeholder="Type something…").strip().lower()
    search_data = ["Sourdough Loaf", "Croissant", "Muffin", "Iced Latte"]
    search_results = [x for x in search_data if query in x.lower()] if query else search_data
    st.markdown("#### Results")
    for item in search_results:
        st.write("•", item)

elif st.session_state.page == 2 and st.session_state.selected_product:
    """Order customisation page.

    Once the user has selected a product on page 1, they arrive here.  They can
    choose the variant (e.g. Mocha vs. Latte), quantity, preferred time slot for
    pickup, and see the resulting price with any applicable discount applied.
    """
    product = st.session_state.selected_product
    st.title(f"Order — {product['Name']}")
    st.image(product["Image"], width=300)

    # Variant selection
    variant = st.selectbox("Select a type", product["Type"])

    # Quantity selection
    quantity = st.number_input("Quantity", min_value=1, max_value=10, step=1, value=1)

    # Time slot selection
    slot = st.selectbox("Preferred time slot", list(time_slots.keys()))
    discount_rate = time_slots[slot]

    # Pricing calculations
    base_price = product["Price"] * quantity
    discount_amount = base_price * discount_rate
    final_price = base_price - discount_amount

    st.markdown(f"**Unit price:** ${product['Price']:.2f}")
    st.markdown(f"**Quantity:** {quantity}")
    st.markdown(f"**Subtotal:** ${base_price:.2f}")
    st.markdown(f"**Discount ({int(discount_rate * 100)}% for {slot}):** -${discount_amount:.2f}")
    st.markdown(f"### Total: ${final_price:.2f}")

    if st.button("Confirm Order"):
        st.success(f"Thank you! Your {product['Name']} ({variant}) will be ready between {slot}.")

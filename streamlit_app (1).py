"""
CTD1D Café – Streamlit demonstration app
This script creates a small café‑style ordering application using the
Streamlit framework.  Users can browse coffee, fruit juice and cake
options, select flavours/variants, add quantities to a cart and then
check out.  A simple pricing engine applies bulk discounts and
time‑based specials (morning combo, afternoon juice or a night‑time
happy hour) before displaying a receipt.  The example illustrates
several core concepts from Streamlit: session state for persisting
data across interactions, widgets for user input, columns to lay
content side by side and custom page configuration.
"""

import streamlit as st
from datetime import datetime


def main() -> None:
    """Main entry point of the café application."""
    # ------------------------------------------------------------------
    # Page configuration
    # Set a title and page icon.  The layout is centered to keep the
    # columns aligned on wider screens.
    st.set_page_config(page_title="CTD1D Café", page_icon="☕", layout="centered")

    st.title("☕ CTD1D Café – Team Streamlit App")
    st.write(
        "Choose your favourite drinks and desserts, add them to the cart "
        "and check out.  Discounts are automatically applied depending on "
        "the time of day."
    )

    # ------------------------------------------------------------------
    # Menu definitions
    # Each category is a dictionary containing a display name, a base price
    # and a list of variants/flavours.  Images are optional – if you wish
    # to display pictures next to each item, add a valid URL in the
    # 'Image' field.  The base price will be adjusted by 10% for bulk
    # purchases of three or more.
    coffee = {
        "Name": "Coffee",
        "Price": 3.0,
        "Type": ["Mocha", "Latte", "Cappuccino"],
        "Image": "https://images.pexels.com/photos/312418/pexels-photo-312418.jpeg",
    }
    frjuice = {
        "Name": "Fruit Juice",
        "Price": 2.0,
        "Type": ["Apple", "Lemon", "Watermelon"],
        "Image": "https://media.istockphoto.com/id/915657126/photo/orange-juice-glass-jar-shot-on-rustic-wooden-table.jpg",
    }
    cake = {
        "Name": "Cake",
        "Price": 6.0,
        "Type": ["Chocolate", "Vanilla", "Cheese"],
        "Image": "https://static.vecteezy.com/system/resources/previews/001/738/638/large_2x/chocolate-cake-slice-free-photo.jpg",
    }
    menu = {"coffee": coffee, "juice": frjuice, "cake": cake}

    # ------------------------------------------------------------------
    # Session state initialisation
    # Streamlit reruns the script on every interaction.  Use
    # st.session_state to preserve variables like the cart and currently
    # selected category across reruns【45687226887764†L67-L75】.  If a key
    # isn't present in session_state it gets initialised here.
    ss = st.session_state
    ss.setdefault("selected_category", None)
    ss.setdefault("cart", {})  # key: (category, name, variant) -> quantity
    ss.setdefault("checkout", False)

    # ------------------------------------------------------------------
    # Category selection
    # Display three columns with images and a button each.  When a button
    # is clicked we store the chosen category in session state and reset
    # the checkout flag.
    cols = st.columns(3)
    for col, key in zip(cols, ["coffee", "juice", "cake"]):
        item = menu[key]
        with col:
            st.image(item["Image"], use_column_width=True)
            if st.button(f"Select {item['Name']}"):
                ss.selected_category = key
                ss.checkout = False
    st.write("\n")

    # ------------------------------------------------------------------
    # Product detail panel
    if ss.selected_category and not ss.checkout:
        item = menu[ss.selected_category]
        st.subheader(f"Ordering {item['Name']}")
        variant = st.selectbox("Choose a flavour", item["Type"])
        quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1, step=1)
        if st.button("Add to cart"):
            key = (ss.selected_category, item["Name"], variant)
            ss.cart[key] = ss.cart.get(key, 0) + quantity
            st.success(f"Added {quantity} × {variant} {item['Name']}")

    # ------------------------------------------------------------------
    # Time‑based discount controls
    # Users can either use the current system time or simulate a different
    # hour via a slider.  Discounts vary by time band: morning (<12),
    # afternoon (12–18) and night (>=18).  A combination of coffee and
    # cake triggers a morning combo discount; fruit juices are discounted
    # in the afternoon; all items get a bigger discount at night.
    with st.expander("Discount settings", expanded=False):
        simulate = st.checkbox("Simulate time", value=True)
        hour = st.slider(
            "Hour of day", 0, 23, datetime.now().hour if not simulate else 9
        )
        time_band = (
            "morning" if hour < 12 else ("afternoon" if hour < 18 else "night")
        )
        st.write(f"Current time band: **{time_band.capitalize()}**")

    # ------------------------------------------------------------------
    # Pricing and receipt generation
    def calculate_totals(cart_dict: dict) -> dict:
        """
        Compute subtotals, discounts and total for the current cart.

        Parameters
        ----------
        cart_dict : dict
            A mapping from (category, name, variant) to quantity.

        Returns
        -------
        dict
            A summary containing per‑item rows and overall totals.
        """
        combo_active = any(k[0] == "coffee" for k in cart_dict) and any(
            k[0] == "cake" for k in cart_dict
        )
        rows = []
        subtotal = discount_sum = total = 0.0
        for (cat_key, name, var), qty in cart_dict.items():
            base_price = menu[cat_key]["Price"]
            line = base_price * qty
            # bulk discount: 10% off if buying three or more of the same variant
            if qty >= 3:
                line *= 0.9
            # time‑based discount percentage
            pct = 0.0
            if time_band == "night":
                pct = 0.30
            elif time_band == "afternoon" and cat_key == "juice":
                pct = 0.20
            elif time_band == "morning" and combo_active and cat_key in {"coffee", "cake"}:
                pct = 0.20
            disc = line * pct
            after = line - disc
            rows.append(
                {
                    "Item": f"{name} – {var}",
                    "Qty": int(qty),
                    "Unit": base_price,
                    "Line subtotal": round(line, 2),
                    "Discount": round(disc, 2),
                    "Line total": round(after, 2),
                }
            )
            subtotal += line
            discount_sum += disc
            total += after
        return {
            "rows": rows,
            "subtotal": round(subtotal, 2),
            "discount": round(discount_sum, 2),
            "total": round(total, 2),
        }

    # ------------------------------------------------------------------
    # Checkout button and receipt display
    # When the user is ready, they click "Proceed to checkout".  The script
    # calculates totals using the helper above and displays a receipt.
    if ss.cart and not ss.checkout:
        if st.button("Proceed to checkout"):
            ss.checkout = True
    if ss.checkout and ss.cart:
        receipt = calculate_totals(ss.cart)
        st.subheader("🧾 Receipt")
        st.table(receipt["rows"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Subtotal", f"${receipt['subtotal']:.2f}")
        col2.metric("Discount", f"-${receipt['discount']:.2f}")
        col3.metric("Total", f"${receipt['total']:.2f}")
        st.success(
            "Thank you for your order! Please PayNow to **1234 567 890**. "
            "Keep this page as your receipt."
        )
        if st.button("Clear cart"):
            ss.cart.clear()
            ss.selected_category = None
            ss.checkout = False
            # rerun the app to reset the UI
            st.experimental_rerun()


if __name__ == "__main__":
    main()

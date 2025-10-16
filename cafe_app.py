"""
Cafe POS Webapp (Variables Section) using Streamlit
--------------------------------------------------

This script implements the *variables* portion of a simple point‑of‑sale web
application for a small cafe.  It is written using the Streamlit library,
which allows you to create interactive web apps with only Python.  The app
allows a cashier or customer to enter quantities for a set of menu items,
optionally apply a voucher code, and it automatically calculates the final
price after applying bulk discounts, voucher discounts and other promotions.

## How it works

1. A **menu** is defined as a list of dictionaries.  Each dictionary
   contains the name of the product and its base price.  For example,
   ``{"name": "Espresso", "price": 3.5}``.  You can freely add or
   remove items from this list – the rest of the program adapts
   automatically.
2. The user enters the quantity of each item they wish to purchase using
   ``st.number_input``.  Quantities are integers and defaults are zero.
3. A text input allows the user to enter a voucher code.  Voucher codes
   are looked up in a dictionary where each code maps to a percentage
   discount on the *subtotal*.
4. The program applies a **bulk discount** for each item if the quantity
   meets a certain threshold.  In this example, buying three or more of
   the same item grants a 10 % discount on that item's cost.
5. **Promotions** can be defined as functions.  For illustration, a
   "Coffee & Muffin" combo gives a fixed $1 discount if at least one coffee
   and one muffin are purchased.
6. The final amount is displayed as a receipt showing line items, totals,
   discounts and the amount due.

The goal of this file is to demonstrate how variables (lists, dictionaries,
functions and numbers) can be used to implement discount logic.  Feel free
to modify the thresholds, discount percentages and promotions to suit your
own business scenario.
"""

import streamlit as st

###############################################################################
# Data definitions
###############################################################################

# Define a simple menu as a list of dictionaries.  Each item has a name and
# base price.  Descriptions can also be added if required.
MENU = [
    {"name": "Coffee", "price": 4.5},
    {"name": "Latte", "price": 5.5},
    {"name": "Muffin", "price": 3.0},
    {"name": "Croissant", "price": 3.5},
]

# Voucher codes map to percentage discounts.  The values represent the
# percentage discount to be applied to the subtotal.  You can add more codes
# or adjust the percentages here.
VOUCHERS = {
    "WELCOME10": 10,  # 10 % off the subtotal
    "FRIEND5": 5,
}

###############################################################################
# Discount and promotion functions
###############################################################################

def apply_bulk_discount(item_price: float, quantity: int) -> float:
    """
    Apply a bulk discount on a single line item.

    For this cafe, buying three or more of the same item gives a 10 % discount.
    The function returns the (possibly) discounted price for that item.

    Parameters
    ----------
    item_price : float
        The base price of the item (without any discount).
    quantity : int
        Number of units purchased.

    Returns
    -------
    float
        The total cost for the item after any bulk discount.
    """
    total = item_price * quantity
    if quantity >= 3:
        discount_rate = 0.10  # 10 %
        total *= (1 - discount_rate)
    return total


def apply_voucher_discount(subtotal: float, code: str) -> float:
    """
    Apply a voucher discount based on a voucher code.

    Looks up the code in the VOUCHERS dictionary and applies the
    corresponding percentage discount to the subtotal.  If the code is not
    valid, no discount is applied.

    Parameters
    ----------
    subtotal : float
        The amount before the voucher is applied.
    code : str
        The voucher code entered by the user.  Codes are case‑insensitive.

    Returns
    -------
    float
        The new subtotal after applying the voucher discount.
    """
    if not code:
        return subtotal
    code = code.strip().upper()
    discount_percent = VOUCHERS.get(code)
    if discount_percent:
        return subtotal * (1 - discount_percent / 100)
    return subtotal


def apply_combo_promotion(cart: dict) -> float:
    """
    Apply a promotion based on multiple items in the cart.

    In this example, if at least one Coffee and one Muffin are purchased,
    deduct a fixed $1 as a combo promotion.  Additional combos do not stack.

    Parameters
    ----------
    cart : dict
        A dictionary mapping item names to quantities.

    Returns
    -------
    float
        The total promotion discount (a positive number representing money
        taken off the subtotal).
    """
    if cart.get("Coffee", 0) >= 1 and cart.get("Muffin", 0) >= 1:
        return 1.0  # flat $1 discount
    return 0.0


###############################################################################
# Calculation logic
###############################################################################

def calculate_totals(cart: dict, voucher_code: str) -> dict:
    """
    Calculate the subtotal, discounts and final total for the current cart.

    Parameters
    ----------
    cart : dict
        Mapping of item names to quantities ordered.
    voucher_code : str
        The voucher code to apply (if any).

    Returns
    -------
    dict
        A dictionary containing the subtotal, bulk_discounted_total,
        voucher_discounted_total, promo_discount, final_total and an itemized
        breakdown for display.
    """
    # Calculate line item totals (with bulk discounts)
    line_items = []
    bulk_total = 0.0
    for item in MENU:
        name = item["name"]
        price = item["price"]
        qty = cart.get(name, 0)
        if qty > 0:
            discounted = apply_bulk_discount(price, qty)
            line_items.append(
                {
                    "name": name,
                    "qty": qty,
                    "unit_price": price,
                    "total": discounted,
                }
            )
            bulk_total += discounted

    # Apply voucher discount
    after_voucher = apply_voucher_discount(bulk_total, voucher_code)

    # Calculate promotion discount (flat amount)
    promo_discount = apply_combo_promotion(cart)
    final_total = after_voucher - promo_discount

    return {
        "line_items": line_items,
        "bulk_total": bulk_total,
        "after_voucher": after_voucher,
        "promo_discount": promo_discount,
        "final_total": final_total,
    }


###############################################################################
# Streamlit user interface
###############################################################################

def main() -> None:
    """Run the Streamlit app."""
    st.set_page_config(page_title="Cafe POS Calculator", page_icon="☕")
    st.title("☕ Café POS Calculator – Discounts & Promotions")
    st.write(
        "Enter the quantity for each item, choose a voucher code if you have one,"
        " and click *Calculate* to see your total with discounts applied."
    )

    # Initialize an empty cart
    cart = {}

    # Layout: each item appears with a number input for quantity
    st.header("Menu Items")
    for item in MENU:
        qty = st.number_input(
            f"{item['name']} (S${item['price']:.2f})",
            min_value=0,
            step=1,
            key=item["name"],
        )
        cart[item["name"]] = int(qty)

    # Voucher input
    voucher_code = st.text_input("Voucher code (optional)")

    # Calculate button
    if st.button("Calculate"):
        result = calculate_totals(cart, voucher_code)
        if not result["line_items"]:
            st.info("Please add at least one item to your cart.")
        else:
            st.subheader("Receipt")
            # Display itemized table
            receipt_rows = []
            for item in result["line_items"]:
                receipt_rows.append(
                    [
                        item["name"],
                        str(item["qty"]),
                        f"S${item['unit_price']:.2f}",
                        f"S${item['total']:.2f}",
                    ]
                )
            st.table(
                {
                    "Item": [row[0] for row in receipt_rows],
                    "Quantity": [row[1] for row in receipt_rows],
                    "Unit Price": [row[2] for row in receipt_rows],
                    "Total": [row[3] for row in receipt_rows],
                }
            )
            # Show summary
            st.write(f"**Subtotal (after bulk discounts):** S${result['bulk_total']:.2f}")
            if voucher_code and result["bulk_total"] != result["after_voucher"]:
                st.write(
                    f"**After voucher '{voucher_code.upper()}':** S${result['after_voucher']:.2f}"
                )
            if result["promo_discount"] > 0:
                st.write(
                    f"**Combo promotion discount:** -S${result['promo_discount']:.2f}"
                )
            st.markdown("---")
            st.success(f"**Final total payable:** S${result['final_total']:.2f}")


if __name__ == "__main__":
    main()
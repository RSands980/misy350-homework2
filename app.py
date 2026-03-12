import streamlit as st
import json
from pathlib import Path
import uuid
import time

st.set_page_config(page_title="Smart Coffee Kiosk", layout="centered")

st.title("Smart Coffee Kiosk Dashboard")
st.subheader("Inventory and Order Management")
st.divider()

inventory_file = Path("inventory.json")
if inventory_file.exists():
    with inventory_file.open("r") as f:
        inventory = json.load(f)
else:
    inventory = []

orders_file = Path("orders.json")
if orders_file.exists():
    with orders_file.open("r") as f:
        orders = json.load(f)
else:
    orders = []

tab1, tab2, tab3, tab4 = st.tabs(["Place Order","View Inventory","Restock","Manage Orders"])

# ---------------- Place Order ----------------
with tab1:
    st.markdown("## Place Order")
    with st.container(border=True):
        item_names = [item["name"] for item in inventory]
        selected_item_name = st.selectbox("Select Item", item_names, key="order_item")
        quantity = st.number_input("Quantity", min_value=1, step=1, key="order_quantity")
        customer_name = st.text_input("Customer Name", key="order_customer")
        place_btn = st.button("Place Order", key="place_btn")

        if place_btn:
            with st.spinner("Placing order..."):
                time.sleep(4)

                selected_item = None
                for item in inventory:
                    if item["name"] == selected_item_name:
                        selected_item = item

                if customer_name == "":
                    st.error("Enter customer name")
                elif selected_item["stock"] < quantity:
                    st.error("Not enough stock")
                else:
                    selected_item["stock"] -= quantity

                    new_order = {
                        "order_id": str(uuid.uuid4())[:8],
                        "customer": customer_name,
                        "item": selected_item_name,
                        "quantity": quantity,
                        "status": "Placed"
                    }

                    orders.append(new_order)

                    with inventory_file.open("w") as f:
                        json.dump(inventory, f, indent=4)

                    with orders_file.open("w") as f:
                        json.dump(orders, f, indent=4)

                    st.success("Order placed successfully!")
                    time.sleep(1)
                    st.rerun()

# ---------------- View Inventory ----------------
with tab2:
    st.markdown("## View Inventory")
    with st.container(border=True):

        view_mode = st.radio("View Mode",["View All","Search"],horizontal=True,key="view_mode")

        if view_mode == "Search":
            search = st.text_input("Search Item", key="search_item")

            filtered_inventory = []
            for item in inventory:
                if search.lower() in item["name"].lower():
                    filtered_inventory.append(item)

            st.dataframe(filtered_inventory)
        else:
            st.dataframe(inventory)

# ---------------- Restock ----------------
with tab3:
    st.markdown("## Restock Inventory")
    with st.container(border=True):

        item_names = [item["name"] for item in inventory]
        restock_item = st.selectbox("Select Item", item_names, key="restock_item")
        restock_amount = st.number_input("Amount to Add", min_value=1, step=1, key="restock_amount")
        restock_btn = st.button("Update Stock", key="restock_btn")

        if restock_btn:
            with st.spinner("Updating stock..."):
                time.sleep(4)

                for item in inventory:
                    if item["name"] == restock_item:
                        item["stock"] += restock_amount

                with inventory_file.open("w") as f:
                    json.dump(inventory, f, indent=4)

                st.success("Stock updated!")
                time.sleep(1)
                st.rerun()

# ---------------- Manage Orders ----------------
with tab4:
    st.markdown("## Manage Orders")
    with st.container(border=True):

        active_orders = []
        for order in orders:
            if order["status"] == "Placed":
                active_orders.append(order)

        if len(active_orders) == 0:
            st.write("No active orders")

        else:
            order_options = []
            for order in active_orders:
                option_text = order["order_id"] + " - " + order["customer"] + " - " + order["item"]
                order_options.append(option_text)

            selected_order_text = st.selectbox("Select Order to Cancel", order_options, key="selected_order")
            cancel_btn = st.button("Cancel Order", key="cancel_btn")

            if cancel_btn:
                with st.spinner("Cancelling order..."):
                    time.sleep(4)

                    selected_order = None
                    for order in active_orders:
                        option_text = order["order_id"] + " - " + order["customer"] + " - " + order["item"]
                        if option_text == selected_order_text:
                            selected_order = order

                    for item in inventory:
                        if item["name"] == selected_order["item"]:
                            item["stock"] += selected_order["quantity"]

                    selected_order["status"] = "Cancelled"

                    with inventory_file.open("w") as f:
                        json.dump(inventory, f, indent=4)

                    with orders_file.open("w") as f:
                        json.dump(orders, f, indent=4)

                    st.success("Order cancelled and stock refunded!")
                    time.sleep(1)
                    st.rerun()
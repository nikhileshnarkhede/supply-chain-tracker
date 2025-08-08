import streamlit as st
from products import products_page
from vendors import vendors_page
from orders import orders_page
import hashlib
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

# MongoDB client (use Streamlit secrets)
client = MongoClient("mongodb://localhost:27017")
db = client["supply_chain"]

# Users and roles
users = {
    "admin": {
        "password": hashlib.sha256("adminpass".encode()).hexdigest(),
        "role": "admin"
    },
    "user1": {
        "password": hashlib.sha256("userpass".encode()).hexdigest(),
        "role": "viewer"
    }
}

# Session state login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# Login screen
if not st.session_state.logged_in:
    st.title("🔐 Login")
    uname = st.text_input("Username")
    passwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if uname in users and users[uname]["password"] == hashlib.sha256(passwd.encode()).hexdigest():
            st.session_state.logged_in = True
            st.session_state.username = uname
            st.session_state.role = users[uname]["role"]
            st.success("✅ Logged in as {}".format(uname))
        else:
            st.error("Invalid credentials")
    st.stop()

# Reset DB Button
if st.sidebar.button("🗑️ Reset Database"):
    db["products"].delete_many({})
    db["vendors"].delete_many({})
    db["orders"].delete_many({})
    st.sidebar.success("✅ Database reset successfully.")

# Main App Interface
st.set_page_config(page_title="Supply Chain Tracker", layout="wide")
st.title("📦 Supply Chain Tracker")

menu = st.sidebar.selectbox("Choose Section", ["Dashboard", "Products", "Vendors", "Orders"])

if menu == "Dashboard":
    st.subheader("📊 Dashboard Overview")
    st.markdown("Welcome, **{}**. Your role is: **{}**.".format(st.session_state.username, st.session_state.role))
    st.markdown("Use the sidebar to navigate.")

    with st.spinner("Loading metrics and charts..."):
        products = list(db["products"].find())
        vendors = list(db["vendors"].find())
        orders = list(db["orders"].find())

        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Total Products", len(products))
        col2.metric("👥 Total Vendors", len(vendors))
        col3.metric("🧾 Total Orders", len(orders))

        st.markdown("### 📦 Stock Overview")
        if products:
            df_products = pd.DataFrame(products)
            st.bar_chart(df_products.set_index("ProductID")["Stock"])

        st.markdown("### 🔁 Order Status Distribution")
        if orders:
            df_orders = pd.DataFrame(orders)
            status_counts = df_orders["Status"].value_counts()
            st.plotly_chart(
                px.pie(names=status_counts.index, values=status_counts.values, title="Order Status")
            )

        st.markdown("### 📉 Products Below Reorder Level")
        if products:
            df_low_stock = df_products[df_products["Stock"] <= df_products["ReorderLevel"]]
            if not df_low_stock.empty:
                st.dataframe(df_low_stock[["ProductID", "Name", "Stock", "ReorderLevel"]])
            else:
                st.success("✅ No products below reorder level.")

        st.markdown("### 📊 Orders per Product")
        if orders:
            product_order_counts = pd.DataFrame(df_orders["ProductID"].value_counts()).reset_index()
            product_order_counts.columns = ["ProductID", "Order Count"]
            st.plotly_chart(
                px.bar(product_order_counts, x="ProductID", y="Order Count", title="Orders per Product")
            )

        st.markdown("### 🏷️ Products per Category")
        if products and "Category" in df_products.columns:
            category_counts = df_products["Category"].value_counts().reset_index()
            category_counts.columns = ["Category", "Count"]
            st.plotly_chart(
                px.bar(category_counts, x="Category", y="Count", title="Products by Category")
            )

        st.markdown("### 🌟 Promising Vendors")
        if products and vendors and orders:
            df_orders = pd.DataFrame(orders)
            df_vendors = pd.DataFrame(vendors)
            df_products = pd.DataFrame(products)

            df_orders["OrderDate"] = pd.to_datetime(df_orders["OrderDate"], errors='coerce')
            df_vendors["ProductCount"] = df_vendors["ProductSupplied"].apply(lambda x: len(x) if isinstance(x, list) else 0)

            vendor_order_counts = df_orders["VendorID"].value_counts().reset_index()
            vendor_order_counts.columns = ["VendorID", "OrderCount"]

            merged = pd.merge(df_vendors, vendor_order_counts, on="VendorID", how="left").fillna(0)
            merged["OrderCount"] = merged["OrderCount"].astype(int)
            merged["Score"] = merged["OrderCount"] * merged["ProductCount"]
            merged["Label"] = merged["Name"] + " (" + merged["VendorID"] + ")"

            fig = px.bar(merged.sort_values(by="Score", ascending=False), x="Label", y="Score",
                         hover_data=["OrderCount", "ProductCount"],
                         title="Promising Vendors by Score (Orders × Products)",
                         labels={"Label": "Vendor", "Score": "Performance Score"})
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📈 Order Summary Insights")
        if orders:
            df_orders["OrderDate"] = pd.to_datetime(df_orders["OrderDate"], errors='coerce')
            df_orders = df_orders.dropna(subset=["OrderDate"])
            df_orders["Month"] = df_orders["OrderDate"].dt.to_period("M").astype(str)

            monthly_order_summary = df_orders.groupby("Month").size().reset_index(name="Order Count")
            st.plotly_chart(
                px.line(monthly_order_summary, x="Month", y="Order Count", markers=True, title="Monthly Order Volume")
            )


            avg_qty_per_vendor = df_orders.groupby("VendorID")["Quantity"].mean().reset_index()
            avg_qty_per_vendor.columns = ["VendorID", "Avg Quantity"]
            st.plotly_chart(
                px.bar(avg_qty_per_vendor, x="VendorID", y="Avg Quantity", title="Average Order Quantity per Vendor")
            )

            heatmap_data = df_orders.groupby(["VendorID", "ProductID"]).size().reset_index(name="Order Count")
            heatmap_pivot = heatmap_data.pivot(index="VendorID", columns="ProductID", values="Order Count").fillna(0)
            st.plotly_chart(
                px.imshow(heatmap_pivot, labels=dict(x="ProductID", y="VendorID", color="Orders"),
                          title="Vendor-Product Order Heatmap")
            )

elif menu == "Products":
    if st.session_state.role == "admin":
        products_page()
    else:
        st.warning("🚫 Access Denied")

elif menu == "Vendors":
    if st.session_state.role == "admin":
        vendors_page()
    else:
        st.warning("🚫 Access Denied")

elif menu == "Orders":
    if st.session_state.role == "admin":
        orders_page()
    else:
        st.warning("🚫 Access Denied")

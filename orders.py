import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# MongoDB client from secrets
client = MongoClient(st.secrets["MONGO_URI"])
db = client["supply_chain"]
orders = db["orders"]
products = db["products"]
vendors = db["vendors"]

def orders_page():
    st.header("Manage Orders")
    product_ids = [p["ProductID"] for p in products.find({}, {"ProductID": 1})]
    vendor_ids = [v["VendorID"] for v in vendors.find({}, {"VendorID": 1})]

    with st.form("Add Order"):
        oid = st.text_input("Order ID")
        pid = st.selectbox("Product ID", options=product_ids)
        vid = st.selectbox("Vendor ID", options=vendor_ids)
        qty = st.number_input("Quantity", min_value=1)
        date = st.date_input("Order Date")
        status = st.selectbox("Status", ["Pending", "Completed"])
        submit_o = st.form_submit_button("Add Order")
        if submit_o:
            orders.insert_one({
                "OrderID": oid,
                "ProductID": pid,
                "VendorID": vid,
                "Quantity": qty,
                "OrderDate": date.strftime("%Y-%m-%d"),
                "Status": status
            })
            st.success("✅ Order Added")

    st.subheader("Current Orders")
    df = pd.DataFrame(list(orders.find()))
    if not df.empty:
        df["OrderID"] = df["OrderID"].astype(str)
        search = st.text_input("Search Order ID")
        if search:
            df = df[df["OrderID"].str.contains(search, case=False)]
        st.dataframe(df)

        to_delete = st.selectbox("Delete Order by ID", df["OrderID"])
        if st.button("Delete Order"):
            orders.delete_one({"OrderID": to_delete})
            st.success("Deleted order: " + str(to_delete))

        to_edit = st.selectbox("Edit Order by ID", df["OrderID"], key="edit_order")
        ord = orders.find_one({"OrderID": to_edit})
        if ord:
            try:
                order_date = datetime.strptime(ord["OrderDate"], "%Y-%m-%d")
            except ValueError:
                try:
                    order_date = datetime.strptime(ord["OrderDate"], "%m/%d/%Y")
                except ValueError:
                    order_date = datetime.today()

            with st.form("Edit Order Form"):
                new_oid = st.text_input("Order ID", value=ord["OrderID"])
                new_pid = st.selectbox("Product ID", options=product_ids, index=product_ids.index(ord["ProductID"]) if ord["ProductID"] in product_ids else 0)
                new_vid = st.selectbox("Vendor ID", options=vendor_ids, index=vendor_ids.index(ord["VendorID"]) if ord["VendorID"] in vendor_ids else 0)
                new_qty = st.number_input("Quantity", value=int(ord["Quantity"]), min_value=1)
                new_date = st.date_input("Order Date", value=order_date)
                new_status = st.selectbox("Status", ["Pending", "Completed"], index=["Pending", "Completed"].index(ord["Status"]))
                submit_edit = st.form_submit_button("Edit Order")
                if submit_edit:
                    orders.update_one(
                        {"OrderID": to_edit},
                        {"$set": {
                            "OrderID": new_oid,
                            "ProductID": new_pid,
                            "VendorID": new_vid,
                            "Quantity": new_qty,
                            "OrderDate": new_date.strftime("%Y-%m-%d"),
                            "Status": new_status
                        }}
                    )
                    st.success("Updated order: " + str(to_edit))

        st.download_button("📅 Download CSV", df.to_csv(index=False), "orders.csv")

    st.subheader("📄 Upload Orders via CSV")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        try:
            csv_df = pd.read_csv(uploaded_file, encoding='utf-8')
            orders.insert_many(csv_df.to_dict(orient="records"))
            st.success("✅ Bulk Orders Uploaded")
        except Exception as e:
            st.error(f"⚠️ Upload failed: {e}")

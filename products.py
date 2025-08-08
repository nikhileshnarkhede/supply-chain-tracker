import streamlit as st
import pandas as pd
from pymongo import MongoClient

# MongoDB client from secrets
client = MongoClient(st.secrets["MONGO_URI"])
db = client["supply_chain"]
products = db["products"]

def products_page():
    st.header("Manage Products")
    with st.form("Add Product"):
        pid = st.text_input("Product ID")
        name = st.text_input("Name")
        category = st.text_input("Category")
        stock = st.number_input("Stock", min_value=0)
        price = st.number_input("Price", min_value=0.0)
        reorder = st.number_input("Reorder Level", min_value=0)
        submit = st.form_submit_button("Add Product")
        if submit:
            products.insert_one({
                "ProductID": pid,
                "Name": name,
                "Category": category,
                "Stock": stock,
                "Price": price,
                "ReorderLevel": reorder
            })
            st.success("✅ Product Added")

    st.subheader("Current Products")
    df = pd.DataFrame(list(products.find()))
    if not df.empty:
        df["ProductID"] = df["ProductID"].astype(str)
        search = st.text_input("Search by Name or ID")
        if search:
            df = df[df["ProductID"].str.contains(search, case=False) | df["Name"].str.contains(search, case=False)]
        st.dataframe(df)

        to_delete = st.selectbox("Delete Product by ID", df["ProductID"])
        if st.button("Delete Product"):
            products.delete_one({"ProductID": to_delete})
            st.success("Deleted product: " + to_delete)

        to_edit = st.selectbox("Edit Product by ID", df["ProductID"], key="edit_product")
        prod = products.find_one({"ProductID": to_edit})
        if prod:
            with st.form("Edit Product Form"):
                new_pid = st.text_input("Product ID", value=prod["ProductID"])
                new_name = st.text_input("Name", value=prod["Name"])
                new_category = st.text_input("Category", value=prod["Category"])
                new_stock = st.number_input("Stock", value=int(prod["Stock"]), min_value=0)
                new_price = st.number_input("Price", value=float(prod["Price"]), min_value=0.0)
                new_reorder = st.number_input("Reorder Level", value=int(prod["ReorderLevel"]), min_value=0)
                submit_edit = st.form_submit_button("Edit Product")
                if submit_edit:
                    products.update_one(
                        {"ProductID": to_edit},
                        {"$set": {
                            "ProductID": new_pid,
                            "Name": new_name,
                            "Category": new_category,
                            "Stock": new_stock,
                            "Price": new_price,
                            "ReorderLevel": new_reorder
                        }}
                    )
                    st.success("Updated product: " + str(to_edit))

        st.download_button("📥 Download CSV", df.to_csv(index=False), "products.csv")

    st.subheader("📤 Upload Products via CSV")
    uploaded_file = st.file_uploader("Upload Product CSV", type="csv", key="product_csv")
    if uploaded_file:
        try:
            product_df = pd.read_csv(uploaded_file, encoding='utf-8')
            products.insert_many(product_df.to_dict(orient="records"))
            st.success("✅ Bulk Products Uploaded")
        except Exception as e:
            st.error(f"⚠️ Upload failed: {e}")

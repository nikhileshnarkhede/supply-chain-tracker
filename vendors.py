import streamlit as st
import pandas as pd
from pymongo import MongoClient

# MongoDB client from secrets
client = MongoClient(st.secrets["MONGO_URI"])
db = client["supply_chain"]
vendors = db["vendors"]
products = db["products"]

def vendors_page():
    st.header("Manage Vendors")
    all_products = [p["ProductID"] for p in products.find({}, {"ProductID": 1})]

    with st.form("Add Vendor"):
        vid = st.text_input("Vendor ID")
        name = st.text_input("Vendor Name")
        contact = st.text_input("Contact Info")
        prod_supplied_multi = st.multiselect("Products Supplied (select one or more)", options=all_products)
        submit_v = st.form_submit_button("Add Vendor")
        if submit_v:
            vendors.insert_one({
                "VendorID": vid,
                "Name": name,
                "ContactInfo": contact,
                "ProductSupplied": prod_supplied_multi
            })
            st.success("✅ Vendor Added")

    st.subheader("Current Vendors")
    df = pd.DataFrame(list(vendors.find()))
    if not df.empty:
        df["VendorID"] = df["VendorID"].astype(str)
        df["ProductSupplied"] = df["ProductSupplied"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
        st.dataframe(df)

        to_delete = st.selectbox("Delete Vendor by ID", df["VendorID"])
        if st.button("Delete Vendor"):
            vendors.delete_one({"VendorID": to_delete})
            st.success("Deleted vendor: " + to_delete)

        to_edit = st.selectbox("Edit Vendor by ID", df["VendorID"], key="edit_vendor")
        vendor_data = vendors.find_one({"VendorID": to_edit})
        if vendor_data:
            with st.form("Edit Vendor Form"):
                new_vid = st.text_input("Vendor ID", value=vendor_data["VendorID"])
                new_name = st.text_input("Vendor Name", value=vendor_data["Name"])
                new_contact = st.text_input("Contact Info", value=vendor_data["ContactInfo"])
                current_supplied = vendor_data.get("ProductSupplied", [])
                if isinstance(current_supplied, str):
                    current_supplied = [current_supplied]
                valid_defaults = [p for p in current_supplied if p in all_products]
                new_products = st.multiselect("Products Supplied", options=all_products, default=valid_defaults)
                submit_edit = st.form_submit_button("Edit Vendor")
                if submit_edit:
                    vendors.update_one(
                        {"VendorID": to_edit},
                        {"$set": {
                            "VendorID": new_vid,
                            "Name": new_name,
                            "ContactInfo": new_contact,
                            "ProductSupplied": new_products
                        }}
                    )
                    st.success("Updated vendor: " + str(to_edit))

        st.download_button("📥 Download CSV", df.to_csv(index=False), "vendors.csv")

    st.subheader("📤 Upload Vendors via CSV")
    uploaded_vendor_file = st.file_uploader("Upload Vendor CSV", type="csv")
    if uploaded_vendor_file:
        try:
            vendor_df = pd.read_csv(uploaded_vendor_file, encoding='utf-8')
            if "ProductSupplied" in vendor_df.columns:
                vendor_df["ProductSupplied"] = vendor_df["ProductSupplied"].apply(lambda x: [i.strip() for i in str(x).split(",")])
            vendors.insert_many(vendor_df.to_dict(orient="records"))
            st.success("✅ Bulk Vendors Uploaded")
        except Exception as e:
            st.error(f"⚠️ Upload failed: {e}")

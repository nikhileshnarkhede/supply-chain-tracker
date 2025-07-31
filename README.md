# 📦 Supply Chain Tracker

A role-based web application built with **Streamlit** and **MongoDB** to manage and visualize products, vendors, and orders in a supply chain. This tool is ideal for stakeholders, warehouse managers, and suppliers to gain insights into supply chain operations and inventory.

---

## ✨ Features

### 🔐 Authentication
- Role-based access:
  - **Admin**: Full access to all functionalities (add/edit/delete/view data).
  - **Viewer**: Read-only access to dashboard.

### 🧾 Modules
- **Products**:
  - Add, edit, delete, and search products.
  - Bulk upload via CSV.
  - Track stock levels and reorder points.
- **Vendors**:
  - Add/edit vendors with linked products.
  - Validate product IDs from the database.
  - Visualize promising vendors based on activity.
- **Orders**:
  - Manage and update order status.
  - View all orders with filters.
  - Import/export orders via CSV.
- **Dashboard**:
  - Visual KPIs: product count, vendor count, order volume.
  - Charts and insights:
    - Stock levels
    - Order status breakdown
    - Products below reorder levels
    - Orders per product
    - Products per category
    - Promising vendors (based on product supply and order activity)
    - Monthly order trends
    - Quantity distribution (box and bar charts)

---

## 🛠️ Tech Stack

| Layer         | Technology         |
|---------------|--------------------|
| Frontend      | Streamlit          |
| Backend       | Python             |
| Database      | MongoDB            |
| Visualizations| Plotly, Streamlit charts |
| Auth          | Basic hashed login |

---

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/nikhileshnarkhede/supply-chain-tracker.git
cd supply-chain-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start MongoDB (locally)
Make sure MongoDB is running at `mongodb://localhost:27017`.

### 4. Launch the app
```bash
streamlit run main_dashboard.py
```

---

## 📁 File Structure

```
├── main_dashboard.py       # Main Streamlit app
├── products.py             # Product management UI
├── vendors.py              # Vendor management UI
├── orders.py               # Orders management UI
├── requirements.txt        # All dependencies
├── data/
│   ├── products.csv        # Sample product data
│   ├── vendors.csv         # Sample vendor data
│   └── orders.csv          # Sample order data
```

---

## 📊 Sample Credentials

| Username | Password   | Role   |
|----------|------------|--------|
| admin    | adminpass  | admin  |
| user1    | userpass   | viewer |

---

## 🔒 Security Note

This app uses basic hashed authentication (`hashlib.sha256`) for demonstration purposes. For production, consider:
- OAuth or JWT tokens
- Role-based access middleware
- Secure password storage (e.g., bcrypt)

---

## 📬 Feedback & Contribution

Have suggestions? Found a bug?  
Feel free to [open an issue](https://github.com/your-username/supply-chain-tracker/issues) or contribute via pull requests.

---

## 📃 License

This project is licensed under the MIT License.
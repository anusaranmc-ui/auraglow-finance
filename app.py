import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Aura Glow - Financial Operating System",
    page_icon="🕯️",
    layout="wide"
)

# --- DATABASE SETUP ---
DB_FILE = "aura_glow_system.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Capital Investments Table
    c.execute('''CREATE TABLE IF NOT EXISTS capital (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    description TEXT,
                    amount REAL)''')
                    
    # Inventory / Raw Materials Table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT UNIQUE,
                    category TEXT,
                    unit TEXT,
                    stock_qty REAL,
                    cost_per_unit REAL)''')
                    
    # Products (Candles & COGS) Table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT UNIQUE,
                    default_price REAL,
                    cogs_unit REAL)''')
                    
    # Sales Orders Table
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    customer TEXT,
                    product_name TEXT,
                    qty INTEGER,
                    unit_price REAL,
                    total_revenue REAL,
                    unit_cogs REAL,
                    total_cogs REAL,
                    net_profit REAL)''')
                    
    # Operating Expenses Table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    description TEXT,
                    amount REAL)''')
                    
    conn.commit()
    conn.close()

init_db()

# --- PDF GENERATOR CLASS ---
class PDFInvoice(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, "AURA GLOW", ln=True, align="C")
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Handcrafted Candles & Scents | Official Receipt", ln=True, align="C")
        self.ln(8)
        self.line(10, 25, 200, 25)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, "Thank you for supporting Aura Glow!", align="C")

def create_pdf(order_id, customer, prod_name, qty, unit_price, total_rev, date_str):
    pdf = PDFInvoice()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, f"Invoice #: AG-{order_id:04d}", ln=False)
    pdf.cell(90, 8, f"Date: {date_str}", ln=True, align="R")
    
    pdf.cell(100, 8, f"Customer: {customer}", ln=True)
    pdf.ln(8)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(80, 8, "Item Description", border=1, fill=True)
    pdf.cell(30, 8, "Qty", border=1, align="C", fill=True)
    pdf.cell(40, 8, "Unit Price (Rs.)", border=1, align="R", fill=True)
    pdf.cell(40, 8, "Total (Rs.)", border=1, align="R", fill=True)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(80, 8, prod_name, border=1)
    pdf.cell(30, 8, str(qty), border=1, align="C")
    pdf.cell(40, 8, f"{unit_price:,.2f}", border=1, align="R")
    pdf.cell(40, 8, f"{total_rev:,.2f}", border=1, align="R")
    pdf.ln()
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(150, 8, "Grand Total:", align="R")
    pdf.cell(40, 8, f"Rs. {total_rev:,.2f}", border=1, align="R")
    
    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🕯️ Aura Glow Finance")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigate System", [
    "📊 Master Dashboard",
    "🛒 Log Sales Order",
    "📦 Raw Materials & Stock",
    "🕯️ Product Costing (BOM)",
    "💸 Expenses & Capital",
    "📑 Custom Date Reports",
    "📄 PDF Invoices & Receipts"
])

# --- MODULE 1: MASTER DASHBOARD ---
if menu == "📊 Master Dashboard":
    st.title("📊 Executive Financial Dashboard")
    st.markdown("Track overall business performance, order profits, and capital recovery position.")

    conn = get_connection()
    df_capital = pd.read_sql("SELECT * FROM capital", conn)
    df_sales = pd.read_sql("SELECT * FROM sales", conn)
    df_expenses = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()

    total_capital = df_capital['amount'].sum() if not df_capital.empty else 0.0
    total_revenue = df_sales['total_revenue'].sum() if not df_sales.empty else 0.0
    total_cogs = df_sales['total_cogs'].sum() if not df_sales.empty else 0.0
    gross_profit = total_revenue - total_cogs
    total_expenses = df_expenses['amount'].sum() if not df_expenses.empty else 0.0
    net_operating_profit = gross_profit - total_expenses
    
    unrecovered_capital = max(0.0, total_capital - net_operating_profit)
    net_position = net_operating_profit - total_capital

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"Rs. {total_revenue:,.2f}")
    c2.metric("Gross Profit", f"Rs. {gross_profit:,.2f}")
    c3.metric("Operating Expenses", f"Rs. {total_expenses:,.2f}")
    c4.metric("Net Operating Profit", f"Rs. {net_operating_profit:,.2f}")

    st.markdown("---")
    st.subheader("🏦 Capital Recovery & Business Position")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Capital Invested", f"Rs. {total_capital:,.2f}")
    col_b.metric("Unrecovered Capital", f"Rs. {unrecovered_capital:,.2f}")
    
    if net_position >= 0:
        col_c.metric("Overall Business Status", f"Rs. {net_position:,.2f}", "PROFITABLE (Capital Recovered)")
    else:
        col_c.metric("Overall Business Status", f"Rs. {net_position:,.2f}", "RECOVERING CAPITAL", delta_color="inverse")

    st.markdown("---")
    st.subheader("📋 Order Profitability Log")
    if not df_sales.empty:
        df_display = df_sales[['id', 'date', 'customer', 'product_name', 'qty', 'total_revenue', 'total_cogs', 'net_profit']].copy()
        df_display['Margin %'] = ((df_display['net_profit'] / df_display['total_revenue']) * 100).round(1)
        st.dataframe(df_display.sort_values(by="id", ascending=False), width="stretch")
    else:
        st.info("No sales orders recorded yet. Use 'Log Sales Order' to start recording transactions.")

# --- MODULE 2: LOG SALES ORDER ---
elif menu == "🛒 Log Sales Order":
    st.title("🛒 Record Sales Order")
    
    conn = get_connection()
    products_df = pd.read_sql("SELECT * FROM products", conn)
    conn.close()

    if products_df.empty:
        st.warning("⚠️ Please create your Candle Products first under 'Product Costing (BOM)' before logging sales.")
    else:
        with st.form("sale_form"):
            col1, col2 = st.columns(2)
            sale_date = col1.date_input("Order Date", date.today())
            customer = col2.text_input("Customer Name / Order ID")
            
            selected_product = col1.selectbox("Select Candle Product", products_df['product_name'].tolist())
            qty = col2.number_input("Quantity Sold", min_value=1, value=1, step=1)
            
            prod_info = products_df[products_df['product_name'] == selected_product].iloc[0]
            unit_cogs = prod_info['cogs_unit']
            default_price = prod_info['default_price']
            
            sale_price = col1.number_input("Selling Price per Unit (Rs.)", value=float(default_price))
            
            total_rev = sale_price * qty
            total_cogs = unit_cogs * qty
            profit = total_rev - total_cogs
            
            st.info(f"**Order Summary:** Total Revenue: **Rs. {total_rev:,.2f}** | Total Cost (COGS): **Rs. {total_cogs:,.2f}** | Net Profit: **Rs. {profit:,.2f}**")
            
            submit = st.form_submit_button("Record Order")
            
            if submit:
                conn = get_connection()
                c = conn.cursor()
                c.execute('''INSERT INTO sales (date, customer, product_name, qty, unit_price, total_revenue, unit_cogs, total_cogs, net_profit)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (sale_date.strftime("%Y-%m-%d"), customer, selected_product, qty, sale_price, total_rev, unit_cogs, total_cogs, profit))
                conn.commit()
                conn.close()
                st.success(f"✅ Order for {customer} logged successfully! Profit: Rs. {profit:,.2f}")

# --- MODULE 3: RAW MATERIALS & STOCK ---
elif menu == "📦 Raw Materials & Stock":
    st.title("📦 Raw Material Purchases & Inventory")
    
    tab1, tab2 = st.tabs(["Add Purchase / Material", "Current Inventory Levels"])
    
    with tab1:
        st.subheader("Log Purchase Outcome")
        with st.form("inv_form"):
            c1, c2 = st.columns(2)
            item_name = c1.text_input("Material Name (e.g., Soy Wax, Glass Jar 200g)")
            category = c2.selectbox("Category", ["Wax", "Fragrance Oil", "Jars/Containers", "Wicks", "Decorative Flowers/Gels", "Packaging"])
            
            unit = c1.selectbox("Measurement Unit", ["grams", "kg", "pcs", "ml", "liters"])
            qty = c2.number_input("Quantity Purchased", min_value=0.01, step=1.0)
            total_cost = c1.number_input("Total Amount Paid (Rs.)", min_value=0.0, step=50.0)
            
            submit_inv = st.form_submit_button("Add to Inventory")
            
            if submit_inv and item_name:
                unit_cost = total_cost / qty
                conn = get_connection()
                c = conn.cursor()
                c.execute('''INSERT INTO inventory (item_name, category, unit, stock_qty, cost_per_unit)
                             VALUES (?, ?, ?, ?, ?)
                             ON CONFLICT(item_name) DO UPDATE SET
                             stock_qty = stock_qty + excluded.stock_qty,
                             cost_per_unit = excluded.cost_per_unit''',
                          (item_name, category, unit, qty, unit_cost))
                conn.commit()
                conn.close()
                st.success(f"✅ Updated inventory for {item_name}. Cost per {unit}: Rs. {unit_cost:,.2f}")

    with tab2:
        st.subheader("Live Raw Material Stock")
        conn = get_connection()
        inv_df = pd.read_sql("SELECT * FROM inventory", conn)
        conn.close()
        if not inv_df.empty:
            st.dataframe(inv_df, width="stretch")
        else:
            st.info("No raw materials registered yet.")

# --- MODULE 4: PRODUCT COSTING (BOM) ---
elif menu == "🕯️ Product Costing (BOM)":
    st.title("🕯️ Candle Product Costing Engine")
    
    with st.form("product_form"):
        c1, c2, c3 = st.columns(3)
        p_name = c1.text_input("Candle Product Name")
        cogs = c2.number_input("Cost to Make 1 Candle - COGS (Rs.)", min_value=0.0, step=10.0)
        price = c3.number_input("Selling Price (Rs.)", min_value=0.0, step=50.0)
        
        submit_p = st.form_submit_button("Save Product")
        
        if submit_p and p_name:
            conn = get_connection()
            c = conn.cursor()
            c.execute('''INSERT INTO products (product_name, default_price, cogs_unit)
                         VALUES (?, ?, ?)
                         ON CONFLICT(product_name) DO UPDATE SET
                         default_price = excluded.default_price,
                         cogs_unit = excluded.cogs_unit''', (p_name, price, cogs))
            conn.commit()
            conn.close()
            st.success(f"✅ Saved product '{p_name}' with Rs. {price - cogs:,.2f} profit margin per unit!")

    st.subheader("Existing Products Catalogue")
    conn = get_connection()
    p_df = pd.read_sql("SELECT * FROM products", conn)
    conn.close()
    if not p_df.empty:
        p_df['Profit Margin / Unit'] = p_df['default_price'] - p_df['cogs_unit']
        p_df['Margin %'] = ((p_df['Profit Margin / Unit'] / p_df['default_price']) * 100).round(1)
        st.dataframe(p_df, width="stretch")

# --- MODULE 5: EXPENSES & CAPITAL ---
elif menu == "💸 Expenses & Capital":
    st.title("💸 Capital Investments & Expenses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏦 Log Capital Investment")
        with st.form("cap_form"):
            cap_date = st.date_input("Investment Date", date.today())
            cap_desc = st.text_input("Description (Equipment, Machinery, Initial Setup)")
            cap_amount = st.number_input("Amount Invested (Rs.)", min_value=0.0, step=1000.0)
            
            if st.form_submit_button("Add Capital"):
                conn = get_connection()
                c = conn.cursor()
                c.execute("INSERT INTO capital (date, description, amount) VALUES (?, ?, ?)",
                          (cap_date.strftime("%Y-%m-%d"), cap_desc, cap_amount))
                conn.commit()
                conn.close()
                st.success("Capital investment logged!")

    with col2:
        st.subheader("📢 Log Operational Expense")
        with st.form("exp_form"):
            exp_date = st.date_input("Expense Date", date.today())
            exp_cat = st.selectbox("Category", ["Marketing/Ads", "Packaging/Boxes", "Electricity/Gas", "Delivery/Courier", "Other"])
            exp_desc = st.text_input("Details")
            exp_amount = st.number_input("Expense Amount (Rs.)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("Add Expense"):
                conn = get_connection()
                c = conn.cursor()
                c.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                          (exp_date.strftime("%Y-%m-%d"), exp_cat, exp_desc, exp_amount))
                conn.commit()
                conn.close()
                st.success("Operational expense logged!")

# --- MODULE 6: CUSTOM DATE REPORTS ---
elif menu == "📑 Custom Date Reports":
    st.title("📑 Custom Time-Period Financial Reports")
    
    c1, c2 = st.columns(2)
    start_date = c1.date_input("Start Date", date(datetime.now().year, 1, 1))
    end_date = c2.date_input("End Date", date.today())
    
    if start_date <= end_date:
        conn = get_connection()
        s_date_str = start_date.strftime("%Y-%m-%d")
        e_date_str = end_date.strftime("%Y-%m-%d")
        
        sales_rep = pd.read_sql(f"SELECT * FROM sales WHERE date BETWEEN '{s_date_str}' AND '{e_date_str}'", conn)
        exp_rep = pd.read_sql(f"SELECT * FROM expenses WHERE date BETWEEN '{s_date_str}' AND '{e_date_str}'", conn)
        conn.close()
        
        period_rev = sales_rep['total_revenue'].sum() if not sales_rep.empty else 0.0
        period_cogs = sales_rep['total_cogs'].sum() if not sales_rep.empty else 0.0
        period_exp = exp_rep['amount'].sum() if not exp_rep.empty else 0.0
        period_net = (period_rev - period_cogs) - period_exp
        
        st.markdown("---")
        st.subheader(f"Financial Summary ({start_date} to {end_date})")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Period Revenue", f"Rs. {period_rev:,.2f}")
        k2.metric("Period COGS", f"Rs. {period_cogs:,.2f}")
        k3.metric("Period Expenses", f"Rs. {period_exp:,.2f}")
        k4.metric("Period Net Profit", f"Rs. {period_net:,.2f}")
        
        st.markdown("---")
        st.write("### Sales Log")
        st.dataframe(sales_rep, width="stretch")
        st.write("### Expense Log")
        st.dataframe(exp_rep, width="stretch")

# --- MODULE 7: PDF INVOICES & RECEIPTS ---
elif menu == "📄 PDF Invoices & Receipts":
    st.title("📄 PDF Invoices & Receipts Generator")
    
    conn = get_connection()
    df_sales = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()

    if df_sales.empty:
        st.info("No sales orders recorded yet to generate receipts.")
    else:
        order_options = [f"Order #{row['id']} - {row['customer']} ({row['product_name']})" for _, row in df_sales.iterrows()]
        selected_option = st.selectbox("Select Order for PDF Receipt", order_options)
        
        selected_id = int(selected_option.split("#")[1].split(" ")[0])
        order_data = df_sales[df_sales['id'] == selected_id].iloc[0]
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.write(f"**Customer:** {order_data['customer']}")
        c1.write(f"**Item:** {order_data['product_name']} x {order_data['qty']}")
        c2.write(f"**Date:** {order_data['date']}")
        c2.write(f"**Total Amount:** Rs. {order_data['total_revenue']:,.2f}")

        pdf_file = create_pdf(
            order_id=order_data['id'],
            customer=order_data['customer'],
            prod_name=order_data['product_name'],
            qty=order_data['qty'],
            unit_price=order_data['unit_price'],
            total_rev=order_data['total_revenue'],
            date_str=order_data['date']
        )

        st.download_button(
            label="⬇️ Download Official PDF Receipt",
            data=pdf_file,
            file_name=f"AuraGlow_Invoice_{order_data['id']}.pdf",
            mime="application/pdf"
        )
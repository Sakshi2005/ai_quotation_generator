import streamlit as st
from datetime import datetime
from fpdf2 import FPDF
import base64
import os
import csv
import random
import pyperclip
import pandas as pd

st.set_page_config(page_title="AI Quotation Generator", layout="centered")

st.title("🧾 AI Quotation Generator")
st.markdown("Generate professional quotations before order placement.")

# --- Sidebar: Company Info ---
st.sidebar.header("📇 Company Information")
company_name = st.sidebar.text_input("Company Name", "Near&Dear Technologies Pvt. Ltd.")
company_email = st.sidebar.text_input("Email", "support@nearanddear.in")
company_phone = st.sidebar.text_input("Phone", "+91-XXXXXXXXXX")

# --- Display Company Info as Header ---
st.markdown(f"""
### 🏢 {company_name}
📧 {company_email}  
📞 {company_phone}
---
""")

# --- Date and Quote Number ---
date = datetime.today().strftime('%B %d, %Y')
quote_no = f"ND-QT-{datetime.today().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

# --- Client Details ---
st.subheader("👤 Client Information")
client_name = st.text_input("Client Name")
client_company = st.text_input("Client Company")
client_email = st.text_input("Client Email")

# --- Quotation Items ---
st.subheader("🛠️ Quotation Items")
items = []
num_items = st.number_input("Number of items", min_value=1, max_value=10, step=1)

for i in range(int(num_items)):
    st.markdown(f"**Item {i+1}**")
    desc = st.text_input(f"Description {i+1}", key=f"desc{i}")
    qty = st.number_input(f"Quantity {i+1}", min_value=1, key=f"qty{i}")
    mrp = st.number_input(f"MRP (Rs.) {i+1}", min_value=0.0, key=f"mrp_{i}")
    discount = st.number_input(f"Discount (%) {i+1}", min_value=0.0, max_value=100.0, value=0.0, key=f"disc{i}")
    gst = st.number_input(f"GST (%) {i+1}", min_value=0.0, max_value=100.0, value=18.0, key=f"gst{i}")

    discounted_rate = mrp * (1 - discount / 100)
    final_rate = discounted_rate * (1 + gst / 100)

    items.append({
        "Description": desc,
        "Qty": qty,
        "MRP": mrp,
        "Discount": discount,
        "GST": gst,
        "Rate": final_rate,
        "Amount": final_rate * qty
    })

# --- TDS and Shipping ---
tds_percent = st.number_input("TDS Deduction (%)", min_value=0.0, max_value=100.0, value=0.0)
shipping_charge = st.number_input("Shipping Charges (Rs.)", min_value=0.0, value=0.0)

# --- Terms & Conditions Input ---
st.subheader("📄 Terms & Conditions")
custom_terms = st.text_area("Enter your custom Terms & Conditions", "- This quotation is valid for 15 days.\n- 50% advance required.\n- Delivery timeline: 7 business days.")

# --- PDF Generator ---
def generate_pdf(items, total, tds_amt, shipping_charge, custom_terms):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"{company_name}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Email: {company_email} | Phone: {company_phone}", ln=True)
    pdf.ln(5)

    pdf.cell(200, 10, txt=f"Quotation No: {quote_no}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {date}", ln=True)
    pdf.cell(200, 10, txt=f"Client: {client_name} ({client_company})", ln=True)
    pdf.cell(200, 10, txt=f"Email: {client_email}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, txt="Description", border=1)
    pdf.cell(15, 10, txt="Qty", border=1)
    pdf.cell(25, 10, txt="MRP", border=1)
    pdf.cell(20, 10, txt="Disc%", border=1)
    pdf.cell(20, 10, txt="GST%", border=1)
    pdf.cell(25, 10, txt="Rate", border=1)
    pdf.cell(35, 10, txt="Amount", border=1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for item in items:
        pdf.cell(50, 10, txt=item['Description'], border=1)
        pdf.cell(15, 10, txt=str(item['Qty']), border=1)
        pdf.cell(25, 10, txt=f"Rs. {item['MRP']:.2f}", border=1)
        pdf.cell(20, 10, txt=f"{item['Discount']}%", border=1)
        pdf.cell(20, 10, txt=f"{item['GST']}%", border=1)
        pdf.cell(25, 10, txt=f"Rs. {item['Rate']:.2f}", border=1)
        pdf.cell(35, 10, txt=f"Rs. {item['Amount']:.2f}", border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Subtotal: Rs. {total:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"TDS Deduction ({tds_percent}%): Rs. {tds_amt:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Shipping Charges: Rs. {shipping_charge:.2f}", ln=True)
    final_total = total - tds_amt + shipping_charge
    pdf.cell(200, 10, txt=f"Grand Total: Rs. {final_total:.2f}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Terms & Conditions:\n{custom_terms}\n\nThank you for considering {company_name}!")
    file_path = f"quotation_{quote_no}.pdf"
    pdf.output(file_path)
    return file_path, final_total

# --- Generate Button and Quotation ---
if st.button("Generate Quotation"):
    if not items or any(not item['Description'] for item in items):
        st.error("Please fill all item descriptions before generating the quotation.")
    else:
        df = pd.DataFrame(items)
        total = df['Amount'].sum()
        tds_amt = total * tds_percent / 100
        final_total = total - tds_amt + shipping_charge

        st.success("Quotation Generated!")
        st.markdown("---")
        st.dataframe(df.style.format({"MRP": "Rs. {:.2f}", "Rate": "Rs. {:.2f}", "Amount": "Rs. {:.2f}"}))

        st.markdown(f"**Subtotal:** Rs. {total:.2f}")
        st.markdown(f"**TDS ({tds_percent}%):** Rs. {tds_amt:.2f}")
        st.markdown(f"**Shipping Charges:** Rs. {shipping_charge:.2f}")
        st.markdown(f"**Grand Total:** Rs. {final_total:.2f}")

        pdf_file, final_total = generate_pdf(items, total, tds_amt, shipping_charge, custom_terms)
        with open(pdf_file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{pdf_file}">📄 Download Quotation PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

        shareable_link = f"Download your quotation: http://localhost:8501/{pdf_file}"
        if st.button("📋 Copy Share Link"):
            pyperclip.copy(shareable_link)
            st.success("Share link copied to clipboard!")

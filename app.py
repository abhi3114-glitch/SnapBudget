import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import ocr_engine
import database

# Page Setup
st.set_page_config(page_title="SnapBudget", layout="wide")

# FAANG-Level CSS
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');

    /* BASE RESET */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #F8FAFC !important;
    }
    
    /* GRADIENT BACKGROUND */
    .stApp {
        background-color: #0F172A;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.1) 0px, transparent 50%);
        background-attachment: fixed;
    }
    
    /* TYPOGRAPHY */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
    }
    
    /* Gradient Text Class */
    .gradient-text {
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* CARDS & GLASSMORPHISM */
    div[data-testid="stForm"], div[data-testid="stDataFrame"], .custom-card, .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    /* ALERTS (Custom Replacements for st.success, st.error) */
    .alert {
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 14px;
        font-weight: 500;
        border: 1px solid transparent;
    }
    .alert-error {
        background-color: rgba(239, 68, 68, 0.2);
        border-color: rgba(239, 68, 68, 0.3);
        color: #FCA5A5;
    }
    .alert-success {
        background-color: rgba(34, 197, 94, 0.2);
        border-color: rgba(34, 197, 94, 0.3);
        color: #86EFAC;
    }
    .alert-info {
        background-color: rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
        color: #93C5FD;
    }
    
    /* INPUT FIELDS */
    div[data-testid="stTextInput"] > div > div, 
    div[data-testid="stNumberInput"] > div > div,
    div[data-testid="stDateInput"] > div > div,
    div[data-testid="stSelectbox"] > div > div {
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid #334155;
        border-radius: 8px;
        color: white;
    }
    
    div[data-testid="stTextInput"] > div > div:focus-within {
        border-color: #38BDF8;
    }

    /* BUTTONS */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2);
        transition: all 0.2s;
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(14, 165, 233, 0.3);
    }

    /* UPLOAD AREA */
    div[data-testid="stFileUploader"] {
        border: 1px dashed rgba(56, 189, 248, 0.4);
        border-radius: 12px;
        padding: 32px;
        background: rgba(30, 41, 59, 0.4);
    }

    /* HIDE DEFAULT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* CUSTOM METRIC */
    .metric-label {
        color: #94A3B8;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #F8FAFC;
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(90deg, #F8FAFC, #CBD5E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Initialize DB
database.init_db()

# --- HEADER ---
col1, col2 = st.columns([1, 6])
with col1:
    # Text logo
    st.markdown("<div style='font-size: 32px; font-weight: 900; color: #38BDF8; text-align: center; margin-top: 10px;'>SB</div>", unsafe_allow_html=True)
with col2:
    st.markdown('<h1 class="gradient-text">SnapBudget</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-top: -15px; font-size: 16px;'>Expense Intelligence</p>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("Menu", ["Upload & Extract", "Dashboard"], label_visibility="collapsed")
    
    st.markdown("---")
    # Pro Tip (Pure HTML)
    st.markdown("""
        <div style='background: rgba(56, 189, 248, 0.05); padding: 16px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.1);'>
            <div style='color: #38BDF8; font-weight: 700; font-size: 12px; margin-bottom: 4px;'>PRO TIP</div>
            <div style='color: #94A3B8; font-size: 13px;'>Drop receipts directly for extraction.</div>
        </div>
    """, unsafe_allow_html=True)

# --- PAGE: UPLOAD ---
if page == "Upload & Extract":
    st.markdown("### New Expense")
    
    uploaded_file = st.file_uploader("Upload Receipt", type=["jpg", "png", "jpeg"], label_visibility="hidden")
    
    if uploaded_file is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("#### Receipt Preview")
            st.image(uploaded_file, caption='Source', width=None, use_container_width=True)
            
        with col2:
            st.markdown("#### Analysis")
            
            with st.spinner("Processing..."):
                try:
                    # OCR
                    image = Image.open(uploaded_file)
                    raw_text = ocr_engine.extract_text(image)
                    
                    if raw_text == "TESSERACT_MISSING":
                        st.markdown('<div class="alert alert-error">Error: Tesseract OCR Engine Not Found</div>', unsafe_allow_html=True)
                    else:
                        extracted_total = ocr_engine.parse_total(raw_text)
                        
                        # Metric Card
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Detected Amount</div>
                            <div class="metric-value">${extracted_total:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Form
                        with st.form("expense_form"):
                            st.write("**Verify & Save**")
                            col_f1, col_f2 = st.columns(2)
                            with col_f1:
                                date_input = st.date_input("Date", datetime.date.today())
                            with col_f2:
                                amount_input = st.number_input("Amount ($)", value=extracted_total, step=0.01, format="%.2f")
                            
                            notes_input = st.text_input("Merchant / Notes") 
                            
                            submitted = st.form_submit_button("Confirm Save")
                            
                            if submitted:
                                full_text = raw_text + f" [NOTES: {notes_input}]"
                                database.add_expense(amount_input, date_input, full_text)
                                st.markdown(f'<div class="alert alert-success">Successfully recorded ${amount_input}</div>', unsafe_allow_html=True)
                        
                        with st.expander("Raw Logs"):
                            st.code(raw_text, language="text")

                except Exception as e:
                    st.markdown(f'<div class="alert alert-error">Analysis Failed: {e}</div>', unsafe_allow_html=True)

# --- PAGE: DASHBOARD ---
elif page == "Dashboard":
    st.markdown("### Financial Overview")
    
    today = datetime.date.today()
    current_month_total = database.get_monthly_total(today.year, today.month)
    
    # Custom Metrics Grid
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; margin-bottom: 32px;">
        <div class="metric-card">
            <div class="metric-label">Current Month Spend</div>
            <div class="metric-value">${current_month_total:,.2f}</div>
            <div style="color: #64748B; font-size: 12px; margin-top: 8px;">{today.strftime('%B %Y')}</div>
        </div>
         <div class="metric-card" style="opacity: 0.7;">
            <div class="metric-label">Budget Status</div>
            <div class="metric-value" style="font-size: 24px; color: #38BDF8;">On Track</div>
             <div style="color: #64748B; font-size: 12px; margin-top: 8px;">Forecast Unavailable</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Recent Transactions")
    
    df = database.get_all_expenses_with_id()
    
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        
        # Table
        edited_df = st.data_editor(
            df,
            column_config={
                "row_index": st.column_config.NumberColumn("ID", width="small", disabled=True),
                "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY", width="medium"),
                "Amount": st.column_config.NumberColumn("Amount", format="$%.2f", width="medium"),
                "Category": st.column_config.SelectboxColumn(
                    "Category", 
                    options=["Uncategorized", "Food", "Transport", "Utilities", "Shopping", "Entertainment"],
                    width="medium"
                ),
                "Raw Text": st.column_config.TextColumn("Details", width="large")
            },
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
            key="expense_editor"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Delete
        with st.expander("Delete Transaction"):
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                row_to_delete = st.number_input("Transaction ID", min_value=1, step=1, label_visibility="collapsed")
            with col_d2:
                if st.button("Delete"):
                    database.delete_expense(row_to_delete)
                    st.rerun()

        # Chart
        try:
            st.markdown("### Spending Trend")
            chart_data = df[['Date', 'Amount']].copy()
            chart_data = chart_data.sort_values('Date')
            st.area_chart(chart_data.set_index('Date'), color=["#38BDF8"])
        except:
             pass
            
    else:
        st.markdown('<div class="alert alert-info">No transactions found.</div>', unsafe_allow_html=True)

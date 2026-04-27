import streamlit as st
import pandas as pd
from datetime import datetime
from core.data_fetcher import get_company_profile, fetch_esg_news, get_suggested_companies
from core.ai_engine import analyze_greenwashing_risk

st.set_page_config(page_title="ESG Risk Terminal", layout="wide", initial_sidebar_state="expanded")

# CSS Injection for Dense Consulting/Terminal Look
st.markdown("""
    <style>
        .stApp { background-color: #0b0f19; color: #e2e8f0; font-family: 'Inter', 'Segoe UI', sans-serif; }
        header, footer { visibility: hidden; }
        [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #374151; }
        
        .header-box { border-bottom: 2px solid #3b82f6; padding-bottom: 10px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: flex-end; }
        .header-title { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 1px;}
        .user-id { color: #10b981; font-size: 11px; text-align: right; font-family: 'Consolas', monospace;}
        
        .panel { background-color: #1f2937; border: 1px solid #374151; border-radius: 6px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
        .panel-title { color: #93c5fd; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; border-bottom: 1px solid #374151; padding-bottom: 5px; letter-spacing: 0.5px;}
        
        .corp-header { display: flex; align-items: center; gap: 15px; }
        .corp-logo { width: 50px; height: 50px; border-radius: 4px; background-color: #fff; padding: 2px;}
        .corp-name { font-size: 22px; font-weight: bold; color: #fff; margin:0;}
        .corp-meta { font-size: 12px; color: #9ca3af; margin:0;}
        
        .metric-grid { display: flex; gap: 10px; }
        .metric-card { flex: 1; background: #111827; border: 1px solid #374151; padding: 10px; border-radius: 4px; text-align: center; }
        .metric-val { font-size: 24px; font-weight: 800; }
        .metric-label { font-size: 10px; color: #9ca3af; text-transform: uppercase; }
        
        /* Data Table override */
        .dataframe { font-size: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# 1. HEADER
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
    <div class="header-box">
        <div>
            <div class="header-title">ESG FORENSIC AUDIT DECK</div>
            <div style="color: #6b7280; font-size: 11px; font-family: 'Consolas', monospace;">DATA: DDGS_ALT_DATA | ENGINE: GROQ_QUANT_LLM</div>
        </div>
        <div class="user-id">
            AUTH: MUHAMMAD FARREL SIDIQ WIJAYA<br>
            LOC: KEPUTIH / ID<br>
            TS: {current_date}
        </div>
    </div>
""", unsafe_allow_html=True)

GENERAL_CLAIMS = "We are committed to net-zero emissions, ethical supply chains, and absolute environmental stewardship across all operations."

# 2. SIDEBAR
with st.sidebar:
    st.markdown("<div class='panel-title'>1. TARGET SELECTION</div>", unsafe_allow_html=True)
    
    # Suggested Universe Feature
    suggestions = get_suggested_companies()
    sugg_options = ["-- Custom Ticker --"] + [s['name'] for s in suggestions]
    selected_sugg = st.selectbox("MOCK UNIVERSE:", sugg_options)
    
    # Auto-fill ticker logic
    default_ticker = ""
    if selected_sugg != "-- Custom Ticker --":
        default_ticker = next(s['ticker'] for s in suggestions if s['name'] == selected_sugg)
        
    ticker = st.text_input("TICKER SYMBOL:", value=default_ticker).upper()
    
    st.markdown("<div class='panel-title' style='margin-top:20px;'>2. AUDIT PARAMETERS</div>", unsafe_allow_html=True)
    input_claim = st.text_area("MANAGEMENT CLAIM (Optional):", height=100)
    final_claim = input_claim if input_claim.strip() != "" else GENERAL_CLAIMS
    
    selected_model = st.selectbox("COMPUTE ENGINE:", ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama-3.3-70b-versatile"])
    run_btn = st.button("GENERATE REPORT", type="primary", use_container_width=True)

# 3. MAIN DASHBOARD
if run_btn and ticker:
    with st.spinner("Extracting alternative data & running LLM forensics..."):
        profile = get_company_profile(ticker)
        news_data = fetch_esg_news(profile['name'])
        audit = analyze_greenwashing_risk(profile['name'], final_claim, news_data, model_name=selected_model)

    # A. Corporate Header Profile
    fallback_logo = "https://via.placeholder.com/50/111827/FFFFFF?text=" + ticker[0:2]
    img_src = profile['logo'] if profile['logo'] else fallback_logo
    
    st.markdown(f"""
        <div class="panel">
            <div class="corp-header">
                <img src="{img_src}" class="corp-logo" onerror="this.src='{fallback_logo}'">
                <div>
                    <p class="corp-name">{profile['name']} ({ticker})</p>
                    <p class="corp-meta">SECTOR: {profile['sector']} | INDUSTRY: {profile['industry']}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2.2])
    
    # B. Left Column: Scores & Metrics
    with col1:
        score = audit.get('overall_risk_score', 0)
        color = "#10b981" if score < 40 else "#f59e0b" if score < 75 else "#ef4444"
        
        st.markdown(f"""
            <div class="panel" style="text-align: center; border-top: 4px solid {color};">
                <div class="panel-title">OVERALL GREENWASHING RISK</div>
                <div style="font-size: 48px; font-weight: 900; color: {color}; line-height: 1;">{score}</div>
                <div style="font-size: 14px; font-weight: bold; color: {color}; margin-bottom: 15px;">{audit.get('risk_level', 'N/A')}</div>
                <div style="background: #111827; padding: 8px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid #374151;">
                    AI VERDICT: {audit.get('verdict', 'N/A')}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Pillar breakdown
        pillars = audit.get('pillar_scores', {})
        st.markdown("<div class='panel'><div class='panel-title'>RISK DECOMPOSITION</div><div class='metric-grid'>", unsafe_allow_html=True)
        for key, val in pillars.items():
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#fff;'>{val}</div><div class='metric-label'>{key}</div></div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # C. Right Column: Analytics & Tables
    with col2:
        st.markdown(f"""
            <div class="panel">
                <div class="panel-title">EXECUTIVE FORENSIC SUMMARY</div>
                <p style="font-size: 14px; color: #e2e8f0; line-height: 1.5; margin:0;">
                    {audit.get('forensic_summary', 'N/A')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Contradiction Table using Pandas for native Streamlit styling
        st.markdown("<div class='panel'><div class='panel-title'>KEY CONTRADICTIONS & EVIDENCE</div>", unsafe_allow_html=True)
        table_data = audit.get('contradiction_table', [])
        if table_data:
            df = pd.DataFrame(table_data)
            df.columns = [col.upper() for col in df.columns]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.write("No specific contradictions structured by AI.")
        st.markdown("</div>", unsafe_allow_html=True)

    # D. Evidence Expander
    with st.expander("VIEW RAW ALTERNATIVE DATA (NEWS SCRAPED)"):
        for n in news_data:
            st.markdown(f"**{n['title']}**<br><span style='font-size:12px; color:#9ca3af;'>{n['body']}</span>", unsafe_allow_html=True)
            st.divider()

else:
    st.markdown("""
        <div style="height: 60vh; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #4b5563;">
            <h2 style="margin:0;">[ AWAITING INPUT ]</h2>
            <p style="font-family: 'Consolas', monospace; font-size: 12px;">Select a ticker from the Mock Universe to begin forensic analysis.</p>
        </div>
    """, unsafe_allow_html=True)
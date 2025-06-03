import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar
import requests
from io import StringIO
from datetime import datetime
import numpy as np

# Page configuration with custom styling
st.set_page_config(
    page_title="Sales Analytics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for impressive styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 10px;
    }
    
    /* Main content area */
    .block-container {
        padding: 2rem 1rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Custom metric cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.1));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: transform 0.3s ease;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #fff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin: 1.5rem 0 1rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .status-done {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
    }
    
    .status-scheduled {
        background: linear-gradient(45deg, #2196F3, #1976D2);
        color: white;
    }
    
    .status-pending {
        background: linear-gradient(45deg, #FF9800, #F57C00);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Success/Info messages */
    .stSuccess {
        background: linear-gradient(45deg, rgba(76, 175, 80, 0.1), rgba(69, 160, 73, 0.1));
        border: 1px solid rgba(76, 175, 80, 0.3);
        border-radius: 10px;
    }
    
    .stInfo {
        background: linear-gradient(45deg, rgba(33, 150, 243, 0.1), rgba(25, 118, 210, 0.1));
        border: 1px solid rgba(33, 150, 243, 0.3);
        border-radius: 10px;
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
</style>
""", unsafe_allow_html=True)

# Function to load data from Google Sheets
@st.cache_data(ttl=300)
def load_google_sheets_data():
    """Load data from Google Sheets with auto-refresh every 5 minutes"""
    try:
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2-ynySfxqoXOra8yMSUO3x5AjlOp42soc2FhE4TySJ9to825OpNCODiIcF70pmv_jI0li4xE5qJ7r/pub?gid=0&single=true&output=csv"
        
        response = requests.get(csv_url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df, None
        else:
            return None, f"Failed to fetch data. Status code: {response.status_code}"
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

# Custom metric card function
def create_metric_card(title, value, icon="📊"):
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with glassmorphism effect
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #667eea; font-weight: 700;">🎯 Control Center</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Data source selection with enhanced styling
    data_source = st.radio(
        "🔗 Choose Data Source:",
        ["Google Sheets (Auto-Update)", "Upload Excel File"],
        help="Select your preferred data source"
    )
    
    if data_source == "Google Sheets (Auto-Update)":
        st.success("✅ Connected to Google Sheets")
        
        current_time = datetime.now().strftime("%H:%M:%S")
        st.info(f"🕐 Auto-refreshes every 5 minutes\nLast checked: {current_time}")
        
        if st.button("🔄 Refresh Now", help="Manually refresh data"):
            st.cache_data.clear()
            st.rerun()
        
        df, error = load_google_sheets_data()
        
        if error:
            st.error(f"❌ {error}")
            st.stop()
        elif df is None:
            st.error("❌ No data loaded from Google Sheets")
            st.stop()
        else:
            st.success(f"✅ Loaded {len(df)} rows from Google Sheets")
    
    else:
        uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
        else:
            df = None

    # Enhanced filters section
    if df is not None and not df.empty:
        if 'Date' not in df.columns:
            st.error("❌ The data does not contain a 'Date' column.")
            st.stop()

        if 'SDR' not in df.columns:
            st.error("❌ The data does not contain a 'SDR' column.")
            st.stop()

        # Parse dates and standardize format
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Formatted Date'] = df['Date'].dt.strftime('%d/%m/%Y')
        df['Month'] = df['Date'].dt.month
        df['Month'] = df['Month'].apply(lambda x: calendar.month_name[int(x)] if pd.notnull(x) else None)
        df['Week'] = df['Date'].dt.isocalendar().week

        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="color: #667eea; font-weight: 600;">🔍 Smart Filters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced filter controls
        col1, col2 = st.columns(2)
        
        with col1:
            sdrs = sorted(df['SDR'].dropna().unique())
            selected_sdr = st.selectbox("👤 SDR", options=["All"] + sdrs)
            
            statuses = sorted(df['Status'].dropna().unique())
            selected_status = st.selectbox("📋 Status", options=["All"] + statuses)
            
            if 'Source' in df.columns:
                sources = sorted(df['Source'].dropna().unique())
                selected_source = st.selectbox("🎯 Source", options=["All"] + sources)
            else:
                selected_source = "All"
        
        with col2:
            if 'Sales Team' in df.columns:
                sales_teams = sorted(df['Sales Team'].dropna().unique())
                selected_sales_team = st.selectbox("👥 Sales Team", options=["All"] + sales_teams)
            else:
                selected_sales_team = "All"

            if 'AE' in df.columns:
                aes = sorted(df['AE'].dropna().unique())
                selected_ae = st.selectbox("🎖️ AE", options=["All"] + aes)
            else:
                selected_ae = "All"
                


        # Date range with enhanced styling
        st.markdown("📊 **Date Range**")
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("From", min_value=min_date, max_value=max_date, value=min_date)
        with col2:
            to_date = st.date_input("To", min_value=min_date, max_value=max_date, value=max_date)

        # Apply filters
        filtered_df = df[
            (df['Date'].dt.date >= from_date) &
            (df['Date'].dt.date <= to_date)
        ]

        if selected_sdr != "All":
            filtered_df = filtered_df[filtered_df['SDR'] == selected_sdr]
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df['Status'] == selected_status]
        if selected_source != "All" and 'Source' in df.columns:
            filtered_df = filtered_df[filtered_df['Source'] == selected_source]
        if selected_sales_team != "All" and 'Sales Team' in df.columns:
            filtered_df = filtered_df[filtered_df['Sales Team'] == selected_sales_team]
        if selected_ae != "All" and 'AE' in df.columns:
            filtered_df = filtered_df[filtered_df['AE'] == selected_ae]


    else:
        filtered_df = None

# Main Dashboard Content
st.markdown('<h1 class="main-title">🚀 Sales Analytics Dashboard</h1>', unsafe_allow_html=True)

# Enhanced status indicator
if df is not None:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if data_source == "Google Sheets (Auto-Update)":
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(76, 175, 80, 0.2); 
                        border-radius: 10px; border: 1px solid rgba(76, 175, 80, 0.5);">
                <span style="color: white; font-weight: 600;">📡 Live Data Connected</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(33, 150, 243, 0.2); 
                        border-radius: 10px; border: 1px solid rgba(33, 150, 243, 0.5);">
                <span style="color: white; font-weight: 600;">📁 File Data Loaded</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        create_metric_card("Total Records", len(df), "📈")
    
    with col3:
        create_metric_card("Filtered Records", len(filtered_df) if filtered_df is not None else 0, "🔍")
    
    with col4:
        if filtered_df is not None and not filtered_df.empty:
            conversion_rate = round((len(filtered_df[filtered_df['Status'].str.lower() == 'done']) / len(filtered_df)) * 100, 1)
            create_metric_card("Conversion Rate", f"{conversion_rate}%", "🎯")

if df is not None and filtered_df is not None:
    
    # Enhanced KPI Section
    if not filtered_df.empty:
        st.markdown('<h2 class="section-title">📊 Key Performance Indicators</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            completed_count = filtered_df[filtered_df['Status'].str.lower() == 'done'].shape[0]
            create_metric_card("Demo Completed", completed_count, "✅")
        
        with col2:
            scheduled_statuses = ['done', 'scheduled', 'rescheduled']
            scheduled_count = filtered_df[filtered_df['Status'].str.lower().isin(scheduled_statuses)].shape[0]
            create_metric_card("Demo Scheduled", scheduled_count, "📅")
        
        with col3:
            if 'Sales Team' in filtered_df.columns:
                team_count = filtered_df['Sales Team'].nunique()
                create_metric_card("Active Teams", team_count, "👥")
            else:
                create_metric_card("Active SDRs", filtered_df['SDR'].nunique(), "👤")
        
        with col4:
            avg_per_day = round(len(filtered_df) / max(1, (to_date - from_date).days + 1), 1)
            create_metric_card("Avg/Day", avg_per_day, "📊")

        # Enhanced Charts Section
        st.markdown('<h2 class="section-title">📈 Analytics & Insights</h2>', unsafe_allow_html=True)
        
        # Status Distribution with enhanced styling
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            status_count = filtered_df['Status'].value_counts().reset_index()
            status_count.columns = ['Status', 'Count']
            
            # Create enhanced bar chart
            fig_bar = px.bar(
                status_count, 
                x='Status', 
                y='Count', 
                title="📊 Status Distribution",
                color='Count',
                color_continuous_scale=['#667eea', '#764ba2', '#f093fb'],
                template='plotly_dark'
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Inter'),
                title_font_size=16,
                showlegend=False
            )
            fig_bar.update_traces(
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>',
                marker_line_width=0
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Industry Distribution Pie Chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if 'Industry' in filtered_df.columns:
                pie_data = filtered_df['Industry'].value_counts().reset_index()
                pie_data.columns = ['Industry', 'Count']
                
                fig_pie = px.pie(
                    pie_data, 
                    names='Industry', 
                    values='Count', 
                    title="🏢 Industry Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    template='plotly_dark'
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', family='Inter'),
                    title_font_size=16
                )
                fig_pie.update_traces(
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("💡 No 'Industry' data available for analysis")
            st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced Sales Team Analysis
        if 'Sales Team' in filtered_df.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            sales_status_counts = filtered_df.groupby(['Sales Team', 'Status']).size().reset_index(name='Count')
            
            fig_sales = px.bar(
                sales_status_counts, 
                x='Sales Team', 
                y='Count', 
                color='Status',
                barmode='group', 
                title="👥 Sales Team Performance Analysis",
                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'],
                template='plotly_dark'
            )
            fig_sales.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Inter'),
                title_font_size=18,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            fig_sales.update_traces(
                hovertemplate='<b>%{x}</b><br>Status: %{legendgroup}<br>Count: %{y}<extra></extra>'
            )
            st.plotly_chart(fig_sales, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced AE Analysis
        if 'AE' in filtered_df.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            ae_status_counts = filtered_df.groupby(['AE', 'Status']).size().reset_index(name='Count')
            
            fig_ae = px.bar(
                ae_status_counts, 
                x='AE', 
                y='Count', 
                color='Status',
                barmode='group', 
                title="🎖️ Account Executive Performance Analysis",
                color_discrete_sequence=['#ff9a9e', '#fecfef', '#fecfef', '#a8edea', '#fed6e3'],
                template='plotly_dark'
            )
            fig_ae.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Inter'),
                title_font_size=18,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            fig_ae.update_traces(
                hovertemplate='<b>%{x}</b><br>Status: %{legendgroup}<br>Count: %{y}<extra></extra>'
            )
            st.plotly_chart(fig_ae, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced Data Table
        st.markdown('<h2 class="section-title">📋 Detailed Data View</h2>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if 'SDR' in filtered_df.columns:
            cols_to_drop = ['SDR','Contact Name','Title','Sales Accepted?','Remarks','Meeting Transcript','Formatted Date',"Month","Week"]
            cols_to_drop = [col for col in cols_to_drop if col in filtered_df.columns]
            display_df = filtered_df.drop(columns=cols_to_drop)
        else:
            display_df = filtered_df
            
        st.dataframe(
            display_df, 
            use_container_width=True,
            height=400
        )
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(255, 193, 7, 0.1); 
                    border-radius: 15px; border: 1px solid rgba(255, 193, 7, 0.3);">
            <h2 style="color: white;">⚠️ No Data Available</h2>
            <p style="color: rgba(255, 255, 255, 0.8);">Please adjust your filters to see results</p>
        </div>
        """, unsafe_allow_html=True)
        
elif data_source == "Upload Excel File":
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2 style="color: white;">📁 Upload Your Data</h2>
        <p style="color: rgba(255, 255, 255, 0.8);">Please upload an Excel file to begin your analysis</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2 style="color: white;">🔄 Loading...</h2>
        <p style="color: rgba(255, 255, 255, 0.8);">Connecting to Google Sheets...</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Footer
if data_source == "Google Sheets (Auto-Update)":
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.1); 
                border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);">
        <span style="color: rgba(255, 255, 255, 0.8);">
            🔄 Dashboard automatically updates every 5 minutes | 📊 Real-time data sync with Google Sheets
        </span>
    </div>
    """, unsafe_allow_html=True)
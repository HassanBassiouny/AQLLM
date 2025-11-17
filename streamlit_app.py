
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pymssql
import os

st.set_page_config(
    page_title="Egypt Air Quality - Real Database",
    page_icon="🇪🇬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

EGYPT_REGIONS = ["Red Sea", "Delta", "Greater Cairo", "Sinai", "New Valley", 
                 "Upper Egypt", "North Coast", "Canal Cities"]

class SecureSynapseConnection:
    def __init__(self):
        try:
            self.server = st.secrets["SYNAPSE_SERVER"]
            self.database = st.secrets["SYNAPSE_DATABASE"]
            self.username = st.secrets["SYNAPSE_USERNAME"]
            self.password = st.secrets["SYNAPSE_PASSWORD"]
            self.connected = True
            self.connection_error = None
        except Exception as e:
            self.connected = False
            self.connection_error = f"Secrets not configured: {str(e)}"
    
    def test_connection(self):
        """Test if we can connect to the database"""
        if not self.connected:
            return False, self.connection_error
            
        try:
            conn = pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database,
                timeout=10
            )
            conn.close()
            return True, "✅ Successfully connected to Azure Synapse"
        except Exception as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    def get_air_quality_data(self, region=None, days=30):
        """Get real data from your Azure Synapse database"""
        if not self.connected:
            return pd.DataFrame()
            
        try:
            conn = pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database,
                timeout=15
            )
            
            # Query to extract numeric values from your data
            base_query = f"""
            SELECT 
                region as Region,
                AVG(TRY_CAST(REPLACE(REPLACE(pm25, ' µg/m³', ''), 'µg/m³', '') as FLOAT)) as PM2_5,
                AVG(TRY_CAST(REPLACE(REPLACE(pm10, ' µg/m³', ''), 'µg/m³', '') as FLOAT)) as PM10,
                AVG(TRY_CAST(REPLACE(REPLACE(no2, ' µg/m³', ''), 'µg/m³', '') as FLOAT)) as NO2,
                AVG(TRY_CAST(REPLACE(REPLACE(co2, ' ppm', ''), 'ppm', '') as FLOAT)) as CO2,
                AVG(TRY_CAST(REPLACE(REPLACE(temperature, ' °C', ''), '°C', '') as FLOAT)) as Temperature,
                AVG(TRY_CAST(REPLACE(REPLACE(humidity, ' %', ''), '%', '') as FLOAT)) as Humidity,
                COUNT(*) as Readings,
                MIN(timestamp) as Period_Start,
                MAX(timestamp) as Period_End
            FROM dbo.IoT_AirQuality
            WHERE CAST(timestamp as DATETIME) >= DATEADD(day, -{days}, GETDATE())
            """
            
            if region and region != "All Regions":
                base_query += f" AND region = '{region}'"
            
            base_query += " GROUP BY region ORDER BY region"
            
            df = pd.read_sql(base_query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            st.error(f"Database query error: {str(e)}")
            return pd.DataFrame()

class AirQualityAI:
    def __init__(self):
        self.region_context = {
            "Red Sea": "Coastal region with tourism and shipping activities",
            "Delta": "Agricultural region with high population density",
            "Greater Cairo": "Urban metropolitan area with traffic and industry", 
            "Sinai": "Desert region with dust storms and tourism",
            "New Valley": "Desert oasis with agricultural activities",
            "Upper Egypt": "Southern region with mixed urban and rural areas",
            "North Coast": "Mediterranean coastal region", 
            "Canal Cities": "Urban areas along Suez Canal with shipping and industry"
        }
    
    def generate_analysis(self, user_prompt, data_df, region, days):
        prompt_lower = user_prompt.lower()
        
        if not data_df.empty:
            summary = f"**📊 Real Data Analysis - {region}**\n\n"
            summary += f"**Data Period**: Last {days} days\n"
            summary += f"**Total Readings**: {data_df['Readings'].sum():,}\n\n"
            
            for _, row in data_df.iterrows():
                pm25_status = "🟢 Good" if row['PM2_5'] <= 12 else "🟡 Moderate" if row['PM2_5'] <= 35 else "🔴 Poor"
                summary += f"**{row['Region']}**: PM2.5: {row['PM2_5']:.1f} μg/m³ ({pm25_status}), Temp: {row['Temperature']:.1f}°C\n"
            
            return summary
        else:
            return "No data available for the selected criteria."

def main():
    st.markdown('<h1 class="main-header">🇪🇬 Egypt Air Quality - Real Database</h1>', unsafe_allow_html=True)
    st.markdown("### 🔗 Connected to Azure Synapse - Live Environmental Data")
    
    # Initialize database connection
    db = SecureSynapseConnection()
    
    # Sidebar
    st.sidebar.header("🎛️ Control Panel")
    
    # Database status
    st.sidebar.subheader("🔌 Database Status")
    if st.sidebar.button("Test Connection"):
        with st.spinner("Testing connection..."):
            success, message = db.test_connection()
            if success:
                st.sidebar.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
            else:
                st.sidebar.markdown(f'<div class="warning-box">{message}</div>', unsafe_allow_html=True)
    
    region = st.sidebar.selectbox("📍 Select Region", ["All Regions"] + EGYPT_REGIONS)
    days = st.sidebar.slider("📅 Analysis Period (Days)", 1, 90, 30)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Tips:**")
    st.sidebar.write("• Make sure database secrets are configured")
    st.sidebar.write("• Test connection first")
    st.sidebar.write("• Data comes from your Azure Synapse")
    
    # Main content
    tab1, tab2 = st.tabs(["📊 Data Analysis", "📈 Visualizations"])
    
    with tab1:
        st.subheader("Real Database Data")
        
        if st.button("🚀 Query Real Database", type="primary"):
            with st.spinner("Fetching real data from Azure Synapse..."):
                data_df = db.get_air_quality_data(region, days)
                
                if not data_df.empty:
                    st.markdown(f'<div class="success-box">✅ Successfully retrieved {len(data_df)} regions from database</div>', unsafe_allow_html=True)
                    
                    # Display metrics
                    st.subheader("📈 Environmental Metrics")
                    cols = st.columns(4)
                    
                    if not data_df.empty:
                        cols[0].metric("Regions", len(data_df))
                        cols[1].metric("Avg PM2.5", f"{data_df['PM2_5'].mean():.1f} μg/m³")
                        cols[2].metric("Avg Temperature", f"{data_df['Temperature'].mean():.1f} °C")
                        cols[3].metric("Total Readings", f"{data_df['Readings'].sum():,}")
                    
                    # Display data
                    st.subheader("📋 Raw Data from Database")
                    st.dataframe(data_df, use_container_width=True)
                    
                    # AI Analysis
                    st.subheader("🤖 AI Analysis")
                    ai = AirQualityAI()
                    analysis = ai.generate_analysis(f"Show data for {region}", data_df, region, days)
                    st.info(analysis)
                    
                else:
                    st.markdown('<div class="warning-box">❌ No data returned from database. Please check your connection and query parameters.</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Data Visualizations")
        
        if st.button("📊 Generate Charts"):
            with st.spinner("Creating visualizations..."):
                data_df = db.get_air_quality_data(region, days)
                
                if not data_df.empty:
                    # PM2.5 Comparison
                    fig1 = px.bar(
                        data_df,
                        x='Region',
                        y='PM2_5',
                        title=f"PM2.5 Levels by Region (Last {days} days)",
                        color='PM2_5',
                        color_continuous_scale=['green', 'yellow', 'red']
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Temperature Comparison
                    fig2 = px.bar(
                        data_df, 
                        x='Region',
                        y='Temperature',
                        title=f"Temperature by Region (Last {days} days)",
                        color='Temperature'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # Multi-metric chart
                    if region == "All Regions":
                        fig3 = px.bar(
                            data_df,
                            x='Region', 
                            y=['PM2_5', 'Temperature'],
                            title=f"Environmental Comparison (Last {days} days)",
                            barmode='group'
                        )
                        st.plotly_chart(fig3, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown("**🌍 Data Source**: Azure Synapse - dbo.IoT_AirQuality")
    st.markdown("**🔒 Security**: Credentials stored securely in Streamlit Secrets")
    st.markdown("**🕒 Real-time**: Live database connection")

if __name__ == "__main__":
    main()

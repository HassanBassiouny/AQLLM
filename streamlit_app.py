
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
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

EGYPT_REGIONS = ["Red Sea", "Delta", "Greater Cairo", "Sinai", "New Valley", 
                 "Upper Egypt", "North Coast", "Canal Cities"]

class SynapseConnection:
    def __init__(self):
        try:
            # Get credentials from Streamlit secrets
            self.server = st.secrets["SYNAPSE_SERVER"]
            self.database = st.secrets["SYNAPSE_DATABASE"]
            self.username = st.secrets["SYNAPSE_USERNAME"]
            self.password = st.secrets["SYNAPSE_PASSWORD"]
            self.connected = True
        except Exception as e:
            self.connected = False
            st.error(f"Secrets configuration error: {str(e)}")
    
    def test_connection(self):
        """Test database connection with better error handling"""
        if not self.connected:
            return False, "Credentials not configured"
            
        try:
            # Try different connection approaches
            conn = pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database,
                login_timeout=10,
                timeout=10
            )
            
            # Test with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 1:
                return True, "✅ Successfully connected to Azure Synapse"
            else:
                return False, "❌ Connection test failed"
                
        except pymssql.OperationalError as e:
            return False, f"❌ Operational Error: {str(e)}"
        except pymssql.InterfaceError as e:
            return False, f"❌ Interface Error: {str(e)}"
        except Exception as e:
            return False, f"❌ Connection Error: {str(e)}"
    
    def get_air_quality_data(self, region=None, days=30):
        """Get real data from Azure Synapse with robust error handling"""
        if not self.connected:
            return pd.DataFrame()
            
        try:
            conn = pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database,
                login_timeout=15,
                timeout=30
            )
            
            # Build the query - using your exact table structure
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
            st.error(f"❌ Database query failed: {str(e)}")
            return pd.DataFrame()

def main():
    st.markdown('<h1 class="main-header">🇪🇬 Egypt Air Quality - Real Database</h1>', unsafe_allow_html=True)
    st.markdown("### 🔗 Connected to Azure Synapse - Live Environmental Data")
    
    # Initialize database connection
    db = SynapseConnection()
    
    # Sidebar
    st.sidebar.header("🎛️ Control Panel")
    
    # Database connection section
    st.sidebar.subheader("🔌 Database Connection")
    
    if st.sidebar.button("🧪 Test Database Connection", use_container_width=True):
        with st.spinner("Testing connection to Azure Synapse..."):
            success, message = db.test_connection()
            if success:
                st.sidebar.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
            else:
                st.sidebar.markdown(f'<div class="warning-box">{message}</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Analysis controls
    region = st.sidebar.selectbox(
        "📍 Select Region", 
        ["All Regions"] + EGYPT_REGIONS,
        help="Choose specific region or compare all regions"
    )
    
    days = st.sidebar.slider(
        "📅 Analysis Period (Days)", 
        1, 90, 30,
        help="Number of days to analyze"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Connection Help")
    st.sidebar.markdown("""
    If connection fails:
    1. Check credentials in Secrets
    2. Verify database is accessible
    3. Ensure firewall allows connections
    4. Test with simple query first
    """)
    
    # Main content
    tab1, tab2 = st.tabs(["📊 Data Analysis", "🔧 Connection Info"])
    
    with tab1:
        st.subheader("Real Environmental Data")
        
        if st.button("🚀 Query Real Database", type="primary", use_container_width=True):
            with st.spinner("Fetching real-time data from Azure Synapse..."):
                data_df = db.get_air_quality_data(region, days)
                
                if not data_df.empty:
                    st.markdown(f'<div class="success-box">✅ Successfully retrieved data for {len(data_df)} regions</div>', unsafe_allow_html=True)
                    
                    # Display summary metrics
                    st.subheader("📈 Summary Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Regions", len(data_df))
                    with col2:
                        avg_pm25 = data_df['PM2_5'].mean()
                        st.metric("Avg PM2.5", f"{avg_pm25:.1f} μg/m³")
                    with col3:
                        avg_temp = data_df['Temperature'].mean()
                        st.metric("Avg Temperature", f"{avg_temp:.1f} °C")
                    with col4:
                        total_readings = data_df['Readings'].sum()
                        st.metric("Total Readings", f"{total_readings:,}")
                    
                    # Display detailed data
                    st.subheader("📋 Detailed Data")
                    st.dataframe(data_df, use_container_width=True)
                    
                    # Data quality info
                    st.subheader("🔍 Data Quality")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Data Period:**")
                        if not data_df.empty:
                            st.write(f"Start: {data_df['Period_Start'].min()}")
                            st.write(f"End: {data_df['Period_End'].max()}")
                    
                    with col2:
                        st.write("**Data Coverage:**")
                        st.write(f"Regions with data: {len(data_df)}")
                        st.write(f"Time range: {days} days")
                    
                else:
                    st.markdown('<div class="warning-box">❌ No data returned from database. Please check:</div>', unsafe_allow_html=True)
                    st.markdown("""
                    1. Database connection credentials
                    2. Network connectivity to Azure Synapse
                    3. Table name and structure
                    4. Data availability for selected period
                    """)
        
        # Quick analysis section
        st.subheader("🤖 Quick Analysis")
        
        if st.button("🌡️ Temperature Analysis", use_container_width=True):
            data_df = db.get_air_quality_data(region, days)
            if not data_df.empty:
                st.info(f"""
                **Temperature Analysis for {region}**
                
                - Average Temperature: **{data_df['Temperature'].mean():.1f}°C**
                - Temperature Range: **{data_df['Temperature'].min():.1f}°C** to **{data_df['Temperature'].max():.1f}°C**
                - Regions with data: **{len(data_df)}**
                - Analysis period: **{days} days**
                
                *Based on real data from Azure Synapse*
                """)
        
        if st.button("🏥 Health Assessment", use_container_width=True):
            data_df = db.get_air_quality_data(region, days)
            if not data_df.empty:
                avg_pm25 = data_df['PM2_5'].mean()
                if avg_pm25 <= 12:
                    status = "🟢 GOOD"
                    recommendation = "Air quality is generally safe for all groups"
                elif avg_pm25 <= 35:
                    status = "🟡 MODERATE" 
                    recommendation = "Sensitive groups should take precautions"
                else:
                    status = "🔴 POOR"
                    recommendation = "Everyone should reduce outdoor activities"
                
                st.info(f"""
                **Health Assessment for {region}**
                
                - PM2.5 Level: **{avg_pm25:.1f} μg/m³** ({status})
                - Recommendation: {recommendation}
                - WHO Guideline: <12 μg/m³ (Good)
                - Regions analyzed: **{len(data_df)}**
                
                *Based on real sensor data*
                """)
    
    with tab2:
        st.subheader("Connection Information")
        
        st.markdown('<div class="info-box">🔒 Your database credentials are stored securely in Streamlit Secrets and are never exposed in the code.</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔧 Required Secrets")
            st.code("""
SYNAPSE_SERVER = "iotsynaps.sql.azuresynapse.net"
SYNAPSE_DATABASE = "your-database-name"
SYNAPSE_USERNAME = "your-username"
SYNAPSE_PASSWORD = "your-password"
            """)
        
        with col2:
            st.markdown("### 📋 Expected Data Structure")
            st.write("**Table:** dbo.IoT_AirQuality")
            st.write("**Columns expected:**")
            st.write("- region (text)")
            st.write("- timestamp (datetime)")
            st.write("- pm25, pm10, no2 (text with units)")
            st.write("- temperature, humidity (text with units)")
            st.write("- co2 (text with units)")
        
        st.markdown("### 🛠️ Troubleshooting")
        st.markdown("""
        **Common Connection Issues:**
        1. **Firewall blocking** - Ensure Azure Synapse allows connections
        2. **Wrong credentials** - Double-check username/password
        3. **Database name** - Verify exact database name
        4. **Network issues** - Check internet connectivity
        
        **To verify manually:**
        - Test connection with SQL Server Management Studio
        - Verify the table exists: `SELECT * FROM dbo.IoT_AirQuality`
        - Check recent data: `SELECT TOP 10 * FROM dbo.IoT_AirQuality ORDER BY timestamp DESC`
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**🌍 Real Data Source**: Azure Synapse Analytics - dbo.IoT_AirQuality")
    st.markdown("**🔐 Security**: Enterprise-grade secure connection")
    st.markdown("**⚡ Performance**: Direct database connectivity")

if __name__ == "__main__":
    main()

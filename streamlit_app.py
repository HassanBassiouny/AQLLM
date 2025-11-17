
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pyodbc
import os

st.set_page_config(
    page_title="Egypt Air Quality",
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
            self.server = st.secrets["SYNAPSE_SERVER"]
            self.database = st.secrets["SYNAPSE_DATABASE"]
            self.username = st.secrets["SYNAPSE_USERNAME"]
            self.password = st.secrets["SYNAPSE_PASSWORD"]
            self.connected = True
        except Exception as e:
            self.connected = False
            st.error(f"Secrets configuration error: {str(e)}")
    
    def get_connection_string(self):
        """Create proper ODBC connection string for Azure Synapse"""
        return f"""
            DRIVER=ODBC Driver 17 for SQL Server;
            SERVER={self.server};
            DATABASE={self.database};
            UID={self.username};
            PWD={self.password};
            Encrypt=yes;
            TrustServerCertificate=no;
            Connection Timeout=30;
        """
    
    def test_connection(self):
        """Test database connection with pyodbc"""
        if not self.connected:
            return False, "Credentials not configured"
            
        try:
            conn_str = self.get_connection_string()
            conn = pyodbc.connect(conn_str)
            
            # Test with simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 1:
                return True, "✅ Successfully connected to Azure Synapse"
            else:
                return False, "❌ Connection test failed"
                
        except pyodbc.InterfaceError as e:
            return False, f"❌ Interface Error: {str(e)}"
        except pyodbc.OperationalError as e:
            return False, f"❌ Operational Error: {str(e)}"
        except Exception as e:
            return False, f"❌ Connection Error: {str(e)}"
    
    def get_air_quality_data(self, region=None, days=30):
        """Get real data from Azure Synapse"""
        if not self.connected:
            return pd.DataFrame()
            
        try:
            conn_str = self.get_connection_string()
            conn = pyodbc.connect(conn_str)
            
            # Build query for your data structure
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
    st.markdown('<h1 class="main-header">🇪🇬 Egypt Air Quality</h1>', unsafe_allow_html=True)
  
    
    # Initialize database connection
    db = SynapseConnection()
    
    # Sidebar
    st.sidebar.header("🎛️ Control Panel")
        
    # Analysis controls
    region = st.sidebar.selectbox(
        "📍 Select Region", 
        ["All Regions"] + EGYPT_REGIONS
    )
    
    days = st.sidebar.slider("📅 Analysis Period (Days)", 1, 90, 30)
    
    
    # Main content
    st.subheader("Egypt Air Quality")
    
    if st.button("🚀 Query Real Database", type="primary", use_container_width=True):
        with st.spinner("Fetching real-time data from Azure Synapse..."):
            data_df = db.get_air_quality_data(region, days)
            
            if not data_df.empty:
                st.markdown(f'<div class="success-box">✅ Successfully retrieved data for {len(data_df)} regions</div>', unsafe_allow_html=True)
                
                # Display summary
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
                
                # Display data
                st.subheader("📋 Detailed Data")
                st.dataframe(data_df, use_container_width=True)
                
                # Create visualizations
                st.subheader("📊 Visualizations")
                
                if region == "All Regions":
                    # Comparison chart
                    fig1 = px.bar(
                        data_df,
                        x='Region',
                        y='PM2_5',
                        title=f"PM2.5 Levels by Region (Last {days} days)",
                        color='PM2_5',
                        color_continuous_scale=['green', 'yellow', 'red']
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Multi-metric chart
                    fig2 = px.bar(
                        data_df,
                        x='Region',
                        y=['PM2_5', 'Temperature'],
                        title=f"Environmental Comparison (Last {days} days)",
                        barmode='group'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    # Single region focus
                    fig = px.bar(
                        data_df,
                        x='Region',
                        y=['PM2_5', 'PM10', 'NO2'],
                        title=f"Pollutant Levels in {region} (Last {days} days)",
                        barmode='group'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.markdown('<div class="warning-box">❌ No data returned from database</div>', unsafe_allow_html=True)
                st.markdown("""
                **Possible issues:**
                1. Check database credentials in Secrets
                2. Verify table exists: `dbo.IoT_AirQuality`
                3. Ensure data exists for selected period
                4. Check network connectivity
                """)
    

if __name__ == "__main__":
    main()

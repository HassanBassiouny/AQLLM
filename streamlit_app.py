import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pyodbc
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
    .chat-container {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        background-color: #f9f9f9;
        max-height: 400px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: right;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: left;
        max-width: 80%;
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

class AirQualityChatbot:
    def __init__(self, db_connection):
        self.db = db_connection
        self.responses = {
            "greeting": [
                "Hello! I'm your Egypt Air Quality assistant. How can I help you today?",
                "Hi there! I can answer questions about air quality in Egypt. What would you like to know?",
                "Welcome! I'm here to provide information about environmental data across Egypt."
            ],
            "regions": [
                "We monitor air quality in these Egyptian regions: Red Sea, Delta, Greater Cairo, Sinai, New Valley, Upper Egypt, North Coast, and Canal Cities.",
                "Our data covers 8 key regions: Red Sea, Delta, Greater Cairo, Sinai, New Valley, Upper Egypt, North Coast, and Canal Cities.",
                "The monitored regions include: Red Sea, Delta, Greater Cairo, Sinai, New Valley, Upper Egypt, North Coast, and Canal Cities."
            ],
            "pollutants": [
                "We track PM2.5, PM10, NO2, CO2, temperature, and humidity levels across Egypt.",
                "Our sensors monitor particulate matter (PM2.5, PM10), nitrogen dioxide (NO2), carbon dioxide (CO2), temperature, and humidity.",
                "Key pollutants monitored: PM2.5 (fine particles), PM10 (coarse particles), NO2 (nitrogen dioxide), CO2 (carbon dioxide), plus temperature and humidity."
            ],
            "data_source": [
                "We use Azure Synapse Analytics to store and process real-time air quality data from IoT sensors across Egypt.",
                "Our data comes from IoT sensors connected to Azure Synapse Analytics for real-time environmental monitoring.",
                "The data is collected from environmental sensors and stored in Azure Synapse Analytics for analysis."
            ],
            "help": [
                "I can help you with: region information, pollutant data, data sources, connection status, and general air quality questions.",
                "Ask me about: monitored regions, pollutants, data sources, or specific air quality metrics.",
                "I can provide information about Egyptian air quality regions, pollutants, data collection methods, and current readings."
            ]
        }
    
    def get_response(self, user_input):
        """Generate chatbot response based on user input"""
        user_input = user_input.lower()
        
        # Greeting detection
        if any(word in user_input for word in ['hello', 'hi', 'hey', 'greetings']):
            return self.responses["greeting"][0]
        
        # Regions query
        elif any(word in user_input for word in ['region', 'area', 'location', 'where']):
            return self.responses["regions"][0]
        
        # Pollutants query
        elif any(word in user_input for word in ['pollutant', 'pm2.5', 'pm10', 'no2', 'co2', 'what measure']):
            return self.responses["pollutants"][0]
        
        # Data source query
        elif any(word in user_input for word in ['data', 'source', 'where data', 'how collect']):
            return self.responses["data_source"][0]
        
        # Help query
        elif any(word in user_input for word in ['help', 'what can you do', 'support']):
            return self.responses["help"][0]
        
        # Connection status
        elif any(word in user_input for word in ['connection', 'connected', 'database', 'synapse']):
            success, message = self.db.test_connection()
            return f"Database Connection Status: {message}"
        
        # Default response
        else:
            return "I'm not sure I understand. Try asking about regions, pollutants, data sources, or type 'help' for assistance."

def main():
    st.markdown('<h1 class="main-header">🇪🇬 Egypt Air Quality - Real Database</h1>', unsafe_allow_html=True)
    st.markdown("### 🔗 Connected to Azure Synapse - Live Environmental Data")
    
    # Initialize database connection and chatbot
    db = SynapseConnection()
    chatbot = AirQualityChatbot(db)
    
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
        ["All Regions"] + EGYPT_REGIONS
    )
    
    days = st.sidebar.slider("📅 Analysis Period (Days)", 1, 90, 30)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 Using pyodbc")
    st.sidebar.markdown("""
    **More reliable for Azure Synapse:**
    - Better ODBC driver support
    - Enterprise-grade connectivity
    - Enhanced error handling
    """)
    
    # Main content - Two columns layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Air Quality Dashboard
        st.subheader("Real Environmental Data from Azure Synapse")
        
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
    
    with col2:
        # Chatbot Section
        st.subheader("💬 Air Quality Assistant")
        st.markdown("Ask me about air quality data, regions, or pollutants!")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Type your message:", placeholder="Ask about air quality...", key="chat_input")
        
        if st.button("Send", key="send_button") and user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get bot response
            bot_response = chatbot.get_response(user_input)
            st.session_state.messages.append({"role": "bot", "content": bot_response})
            
            # Rerun to update chat display
            st.rerun()
        
        # Quick action buttons
        st.markdown("**Quick Questions:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Regions 📍", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What regions do you monitor?"})
                bot_response = chatbot.get_response("regions")
                st.session_state.messages.append({"role": "bot", "content": bot_response})
                st.rerun()
            
            if st.button("Pollutants 🌫️", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What pollutants do you measure?"})
                bot_response = chatbot.get_response("pollutants")
                st.session_state.messages.append({"role": "bot", "content": bot_response})
                st.rerun()
        
        with col2:
            if st.button("Data Source 📊", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Where does the data come from?"})
                bot_response = chatbot.get_response("data source")
                st.session_state.messages.append({"role": "bot", "content": bot_response})
                st.rerun()
            
            if st.button("Connection 🔌", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Check database connection"})
                bot_response = chatbot.get_response("connection")
                st.session_state.messages.append({"role": "bot", "content": bot_response})
                st.rerun()
        
        # Clear chat button
        if st.button("Clear Chat 🗑️", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Connection info
    with st.expander("🔧 Connection Details"):
        st.markdown("""
        **Using pyodbc with ODBC Driver 17 for SQL Server**
        
        **Required Secrets:**
        ```toml
        SYNAPSE_SERVER = "iotsynaps.sql.azuresynapse.net"
        SYNAPSE_DATABASE = "your-database-name"
        SYNAPSE_USERNAME = "your-username"
        SYNAPSE_PASSWORD = "your-password"
        ```
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**🌍 Data Source**: Azure Synapse Analytics - dbo.IoT_AirQuality")
    st.markdown("**🔧 Connection**: pyodbc with ODBC Driver 17")
    st.markdown("**🔒 Security**: Encrypted connection")

if __name__ == "__main__":
    main()

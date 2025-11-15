
import gradio as gr
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pyodbc
import os

# Your Egyptian regions
EGYPT_REGIONS = ["Red Sea", "Delta", "Greater Cairo", "Sinai", "New Valley", 
                 "Upper Egypt", "North Coast", "Canal Cities"]

# Real Synapse Database Connection
class SynapseConnection:
    def __init__(self):
        # Get credentials from Railway environment variables
        self.server = os.getenv('SYNAPSE_SERVER', 'iotsynaps.sql.azuresynapse.net')
        self.database = os.getenv('SYNAPSE_DATABASE', 'your-database-name')
        self.username = os.getenv('SYNAPSE_USERNAME', 'your-username')
        self.password = os.getenv('SYNAPSE_PASSWORD', 'your-password')
    
    def get_connection_string(self):
        return f"""
            Driver={{ODBC Driver 17 for SQL Server}};
            Server={self.server};
            Database={self.database};
            Uid={self.username};
            Pwd={self.password};
            Encrypt=yes;
            TrustServerCertificate=no;
            Connection Timeout=30;
        """
    
    def execute_query(self, query):
        """Execute SQL query and return DataFrame"""
        try:
            print(f"🔍 Executing query: {query[:100]}...")
            conn = pyodbc.connect(self.get_connection_string())
            df = pd.read_sql(query, conn)
            conn.close()
            print(f"✅ Query successful, returned {len(df)} rows")
            return df
        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

# Database Queries Class
class AirQualityQueries:
    def __init__(self):
        self.db = SynapseConnection()
    
    def get_air_quality_summary(self, region=None, days=30):
        """Get REAL air quality data from Azure Synapse"""
        base_query = f"""
        SELECT 
            region as Region,
            AVG(CAST(REPLACE(REPLACE(pm25, ' µg/m³', ''), 'µg/m³', '') as FLOAT)) as Avg_PM2_5,
            AVG(CAST(REPLACE(REPLACE(pm10, ' µg/m³', ''), 'µg/m³', '') as FLOAT)) as Avg_PM10,
            AVG(CAST(REPLACE(REPLACE(no2, ' µg/m³', ''), 'µg/m³', '') as FLOAT)) as Avg_NO2,
            AVG(CAST(REPLACE(REPLACE(co2, ' ppm', ''), 'ppm', '') as FLOAT)) as Avg_CO2,
            AVG(CAST(REPLACE(REPLACE(temperature, ' °C', ''), '°C', '') as FLOAT)) as Avg_Temperature,
            AVG(CAST(REPLACE(REPLACE(humidity, ' %', ''), '%', '') as FLOAT)) as Avg_Humidity,
            COUNT(*) as Readings_Count,
            MIN(timestamp) as Period_Start,
            MAX(timestamp) as Period_End
        FROM dbo.IoT_AirQuality
        WHERE CAST(timestamp as DATETIME) >= DATEADD(day, -{days}, GETDATE())
        """
        
        if region and region != "All Regions":
            base_query += f" AND region = '{region}'"
        
        base_query += " GROUP BY region ORDER BY region"
        
        return self.db.execute_query(base_query)
    
    def get_pollutant_trends(self, region, pollutant='pm25', days=30):
        """Get trend data for specific pollutant"""
        pollutant_clean = f"CAST(REPLACE(REPLACE({pollutant}, ' µg/m³', ''), 'µg/m³', '') as FLOAT)"
        
        query = f"""
        SELECT 
            CAST(timestamp AS DATE) as Date,
            AVG({pollutant_clean}) as Avg_Pollutant,
            COUNT(*) as Readings
        FROM dbo.IoT_AirQuality
        WHERE CAST(timestamp AS DATETIME) >= DATEADD(day, -{days}, GETDATE())
          AND region = '{region}'
        GROUP BY CAST(timestamp AS DATE)
        ORDER BY Date
        """
        
        return self.db.execute_query(query)
    
    def get_available_regions(self):
        """Get list of regions from database"""
        query = "SELECT DISTINCT region FROM dbo.IoT_AirQuality ORDER BY region"
        try:
            regions_df = self.db.execute_query(query)
            return regions_df['region'].tolist()
        except:
            return EGYPT_REGIONS

# Smart AI Response Generator
class SmartAIResponder:
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
    
    def generate_response(self, data_context, user_prompt):
        prompt_lower = user_prompt.lower()
        
        if any(word in prompt_lower for word in ['temperature', 'temp', 'hot', 'cold']):
            return self._generate_temperature_response(data_context, user_prompt)
        elif any(word in prompt_lower for word in ['compare', 'comparison', 'versus', 'vs']):
            return self._generate_comparison_response(data_context, user_prompt)
        elif any(word in prompt_lower for word in ['health', 'risk', 'safe', 'danger']):
            return self._generate_health_response(data_context, user_prompt)
        elif any(word in prompt_lower for word in ['region', 'area', 'location']):
            return self._generate_region_response(data_context, user_prompt)
        else:
            return self._generate_general_response(data_context, user_prompt)
    
    def _generate_temperature_response(self, data_context, user_prompt):
        return f"""🌡️ **Temperature Analysis - REAL DATA**

{data_context}

**Insights from Actual Measurements:**
- Analysis based on real sensor data from Azure Synapse
- Temperature patterns reflect actual environmental conditions
- Regional variations show true geographical influences

*Based on your question: "{user_prompt}"*"""
    
    def _generate_comparison_response(self, data_context, user_prompt):
        return f"""📊 **Regional Comparison - REAL DATA**

{data_context}

**Data-Driven Analysis:**
- Direct comparison of actual environmental measurements
- Real sensor data enables accurate regional assessment
- Evidence-based environmental intelligence

*Comparison based on: "{user_prompt}"*"""
    
    def _generate_health_response(self, data_context, user_prompt):
        return f"""🏥 **Health Impact Assessment - REAL DATA**

{data_context}

**WHO Guidelines Applied to Real Data:**
- PM2.5: Good (0-12 μg/m³), Moderate (12-35 μg/m³), Poor (>35 μg/m³)
- PM10: Good (0-50 μg/m³), Moderate (50-100 μg/m³), Poor (>100 μg/m³)

**Evidence-Based Recommendations:**
- Real-time data enables precise health guidance
- Regional-specific recommendations based on actual conditions
- Continuous monitoring supports timely interventions

*Health analysis for: "{user_prompt}"*"""
    
    def _generate_general_response(self, data_context, user_prompt):
        return f"""🤖 **Environmental Intelligence - REAL DATA**

{data_context}

**Comprehensive Analysis:**
Real environmental data from Azure Synapse enables accurate assessment and informed decision-making across Egyptian regions.

*Analysis based on: "{user_prompt}"*"""

# Main Analyzer Class
class AirQualityAnalyzer:
    def __init__(self):
        self.queries = AirQualityQueries()
        self.ai_responder = SmartAIResponder()
    
    def prepare_data_context(self, region=None, days=30):
        """Prepare data context from REAL database"""
        try:
            summary_df = self.queries.get_air_quality_summary(region, days)
            
            context = "## 🌍 Egypt Air Quality - LIVE DATABASE DATA\n\n"
            context += f"**📊 Data Source**: Azure Synapse SQL Pool\n"
            context += f"**📅 Analysis Period**: Last {days} days\n"
            context += f"**🕒 Last Query**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if summary_df.empty:
                context += "⚠️ *No data found for the specified criteria*\n\n"
                return context
            
            for _, row in summary_df.iterrows():
                pm25_status = "🟢 Good" if row['Avg_PM2_5'] <= 12 else "🟡 Moderate" if row['Avg_PM2_5'] <= 35 else "🔴 Poor"
                pm10_status = "🟢 Good" if row['Avg_PM10'] <= 50 else "🟡 Moderate" if row['Avg_PM10'] <= 100 else "🔴 Poor"
                
                context += f"""### 📍 {row['Region']}
**Environmental Metrics:**
• 🌡️ **Temperature**: {row['Avg_Temperature']:.1f} °C
• 💧 **Humidity**: {row['Avg_Humidity']:.1f} %
• 🌫️ **PM2.5**: {row['Avg_PM2_5']:.1f} μg/m³ ({pm25_status})
• 🏭 **PM10**: {row['Avg_PM10']:.1f} μg/m³ ({pm10_status})
• 🚗 **NO2**: {row['Avg_NO2']:.1f} μg/m³
• 🌿 **CO2**: {row['Avg_CO2']:.1f} ppm
• 📊 **Readings**: {row['Readings_Count']:,}
• **Period**: {row['Period_Start']} to {row['Period_End']}

"""
            
            return context
            
        except Exception as e:
            return f"## ❌ Database Connection Error\n\nUnable to connect to Azure Synapse.\n\n**Error**: {str(e)}\n\nPlease check your database credentials."
    
    def create_visualization(self, region, days=30):
        """Create visualization from REAL data"""
        try:
            if region == "All Regions":
                summary_df = self.queries.get_air_quality_summary(region, days)
                if summary_df.empty:
                    return None
                
                fig = px.bar(
                    summary_df,
                    x='Region',
                    y=['Avg_PM2_5', 'Avg_Temperature'],
                    title=f"📊 Real Data - Environmental Comparison (Last {days} days)",
                    barmode='group',
                    labels={'value': 'Measurement', 'variable': 'Parameter'},
                    color_discrete_map={'Avg_PM2_5': '#FF6B6B', 'Avg_Temperature': '#4ECDC4'}
                )
            else:
                trend_data = self.queries.get_pollutant_trends(region, 'pm25', days)
                if trend_data.empty:
                    return None
                
                fig = px.line(
                    trend_data,
                    x='Date',
                    y='Avg_Pollutant',
                    title=f"📈 Real Data - PM2.5 Trend in {region} (Last {days} days)"
                )
            
            fig.update_layout(showlegend=True)
            return fig
            
        except Exception as e:
            print(f"Visualization error: {e}")
            return None
    
    def analyze(self, user_prompt, region, days, use_ai):
        """Main analysis function using REAL data"""
        data_context = self.prepare_data_context(region, days)
        visualization = self.create_visualization(region, days)
        
        if use_ai:
            analysis = self.ai_responder.generate_response(data_context, user_prompt)
        else:
            analysis = f"## 📊 REAL DATABASE DATA\n\n{data_context}\n\n**Your Question:** {user_prompt}"
        
        return analysis, visualization

# Initialize analyzer
analyzer = AirQualityAnalyzer()

# Gradio interface function
def analyze_air_quality(prompt, region, days, use_ai):
    try:
        return analyzer.analyze(prompt, region, days, use_ai)
    except Exception as e:
        return f"❌ System Error: {str(e)}", None

# Build the Gradio interface
with gr.Blocks(
    theme=gr.themes.Soft(),
    title="Egypt Air Quality - Real Database Dashboard"
) as demo:
    
    gr.Markdown("""
    # 🇪🇬 Egypt Air Quality Dashboard
    ### 🔗 Connected to Azure Synapse - REAL Database Data
    *Live environmental data from IoT sensors across Egypt*
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎛️ Control Panel")
            
            region_input = gr.Dropdown(
                choices=["All Regions"] + EGYPT_REGIONS,
                label="📍 Select Region", 
                value="All Regions",
                info="Real data from Azure Synapse"
            )
            
            days_input = gr.Slider(
                minimum=1, maximum=90, value=30,
                label="📅 Analysis Period (Days)",
                info="Query real historical data"
            )
            
            ai_toggle = gr.Checkbox(
                label="🤖 AI Analysis", 
                value=True,
                info="Get insights from real data"
            )
            
            analyze_btn = gr.Button("🚀 Query Real Database", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 🔧 Database Connection
            - **Status**: Connected to Azure Synapse
            - **Table**: dbo.IoT_AirQuality
            - **Data**: Real-time sensor readings
            - **Update**: Live database queries
            """)
            
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(
                lines=4,
                label="💬 Ask About Real Environmental Data",
                placeholder="Examples:\n• 'Show current air quality from real sensors'\n• 'Compare actual PM2.5 levels across regions'\n• 'Temperature trends from database'\n• 'Health risks based on real measurements'",
            )
    
    with gr.Row():
        output_text = gr.Markdown(
            label="📋 Analysis Results - LIVE DATABASE",
            show_copy_button=True
        )
    
    with gr.Row():
        output_plot = gr.Plot(
            label="📊 Real Data Visualization",
            show_label=True
        )

    examples = gr.Examples(
        examples=[
            ["Show real air quality data for all regions", "All Regions", 30, True],
            ["What are the actual temperature readings in Delta?", "Delta", 7, True],
            ["Compare real pollution levels across Egypt", "All Regions", 30, True],
            ["Health assessment based on real sensor data", "Greater Cairo", 7, True]
        ],
        inputs=[prompt_input, region_input, days_input, ai_toggle],
        label="🚀 Real Database Queries"
    )
    
    analyze_btn.click(
        fn=analyze_air_quality,
        inputs=[prompt_input, region_input, days_input, ai_toggle],
        outputs=[output_text, output_plot]
    )

    gr.Markdown("""
    ---
    **🌍 Data Source**: Azure Synapse SQL Pool - dbo.IoT_AirQuality  
    **📊 Real Sensor Data**: Live environmental monitoring  
    **🔗 Connection**: Direct database integration  
    **🎯 Purpose**: Real-time environmental intelligence
    """)

# Get port from Railway environment or default to 7860
port = int(os.getenv("PORT", 7860))

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )

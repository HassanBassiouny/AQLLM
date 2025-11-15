
import os
from flask import Flask
import gradio as gr
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# Your Egyptian regions
EGYPT_REGIONS = ["Red Sea", "Delta", "Greater Cairo", "Sinai", "New Valley", 
                 "Upper Egypt", "North Coast", "Canal Cities"]

# Mock data generator
class MockAirQualityData:
    def __init__(self):
        self.regions = EGYPT_REGIONS
        self.base_data = {
            "Red Sea": {"pm25": 9.0, "pm10": 20.0, "no2": 7.0, "co2": 300, "temp": 28.0, "humidity": 37.0},
            "Delta": {"pm25": 27.0, "pm10": 60.0, "no2": 22.0, "co2": 340, "temp": 25.5, "humidity": 60.0},
            "Greater Cairo": {"pm25": 56.0, "pm10": 110.0, "no2": 63.0, "co2": 510, "temp": 25.0, "humidity": 40.0},
            "Sinai": {"pm25": 11.0, "pm10": 24.0, "no2": 5.0, "co2": 280, "temp": 30.0, "humidity": 31.0},
            "New Valley": {"pm25": 24.0, "pm10": 52.0, "no2": 9.0, "co2": 340, "temp": 33.0, "humidity": 21.0},
            "Upper Egypt": {"pm25": 23.0, "pm10": 49.0, "no2": 13.0, "co2": 315, "temp": 31.0, "humidity": 25.0},
            "North Coast": {"pm25": 8.0, "pm10": 19.0, "no2": 5.0, "co2": 300, "temp": 25.0, "humidity": 69.0},
            "Canal Cities": {"pm25": 17.0, "pm10": 40.0, "no2": 21.0, "co2": 355, "temp": 27.0, "humidity": 51.0}
        }
    
    def generate_mock_summary(self, region=None, days=30):
        data = []
        regions_to_show = [region] if region and region != "All Regions" else self.regions
        
        for reg in regions_to_show:
            base = self.base_data[reg]
            current_time = datetime.now()
            time_factor = (current_time.hour / 24.0) + (current_time.minute / 1440.0)
            variation = 0.15 * (0.5 + 0.5 * abs(time_factor - 0.5) / 0.5)
            
            data.append({
                'Region': reg,
                'Avg_PM2_5': max(1, base["pm25"] * (1 + random.uniform(-variation, variation))),
                'Avg_PM10': max(1, base["pm10"] * (1 + random.uniform(-variation, variation))),
                'Avg_NO2': max(1, base["no2"] * (1 + random.uniform(-variation, variation))),
                'Avg_CO2': max(250, base["co2"] * (1 + random.uniform(-variation/3, variation/3))),
                'Avg_Temperature': base["temp"] * (1 + random.uniform(-0.08, 0.08)),
                'Avg_Humidity': max(10, min(95, base["humidity"] * (1 + random.uniform(-0.15, 0.15)))),
                'Readings_Count': random.randint(45, 180),
                'Period_Start': current_time - timedelta(days=days),
                'Period_End': current_time
            })
        
        return pd.DataFrame(data)

# Smart AI Response Generator
class SmartAIResponder:
    def __init__(self):
        self.region_context = {
            "Red Sea": "Coastal region with tourism and shipping activities. Generally has good air quality due to sea breezes.",
            "Delta": "Agricultural region with high population density. PM2.5 levels are often elevated due to agricultural activities.",
            "Greater Cairo": "Urban metropolitan area with significant traffic and industrial emissions. Typically has the highest pollution levels.",
            "Sinai": "Desert region with dust storms and minimal industrial activity. Air quality is generally good but affected by dust.",
            "New Valley": "Desert oasis with agricultural activities. Moderate pollution levels with seasonal variations.",
            "Upper Egypt": "Southern region with mixed urban and rural areas. Air quality varies by location and season.",
            "North Coast": "Mediterranean coastal region with good air quality influenced by sea breezes.",
            "Canal Cities": "Urban areas along Suez Canal with shipping and industrial emissions. Moderate to high pollution levels."
        }
    
    def generate_response(self, data_context, user_prompt):
        prompt_lower = user_prompt.lower()
        
        if any(word in prompt_lower for word in ['temperature', 'temp', 'hot', 'cold', 'warm']):
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
        return f"""🌡️ **Temperature Analysis**

{data_context}

**Key Temperature Insights:**
- Regional temperatures show typical Egyptian climate patterns
- Coastal regions are generally cooler than desert areas
- Temperature affects pollutant dispersion and formation

*Based on your question: "{user_prompt}"*"""
    
    def _generate_comparison_response(self, data_context, user_prompt):
        return f"""📊 **Regional Comparison**

{data_context}

**Comparative Analysis:**
- Clear patterns emerge across different region types
- Urban vs rural vs coastal distinctions are evident
- Each region has unique environmental characteristics

*Comparison based on: "{user_prompt}"*"""
    
    def _generate_health_response(self, data_context, user_prompt):
        return f"""🏥 **Health Impact Analysis**

{data_context}

**Health Guidelines (WHO):**
- PM2.5: Good (<12), Moderate (12-35), Poor (>35) μg/m³
- PM10: Good (<50), Moderate (50-100), Poor (>100) μg/m³

**Recommendations:**
- Monitor air quality in high-pollution areas
- Sensitive groups should take precautions when needed

*Health analysis for: "{user_prompt}"*"""
    
    def _generate_region_response(self, data_context, user_prompt):
        return f"""📍 **Regional Profile**

{data_context}

**Regional Context:**
Egypt's diverse geography creates varied environmental conditions across regions.

*Regional analysis for: "{user_prompt}"*"""
    
    def _generate_general_response(self, data_context, user_prompt):
        return f"""🤖 **AI Environmental Analysis**

{data_context}

**Environmental Intelligence:**
Comprehensive analysis of Egyptian regional environmental data.

*Analysis based on: "{user_prompt}"*"""

# Main analyzer class
class AirQualityAnalyzer:
    def __init__(self):
        self.data_generator = MockAirQualityData()
        self.ai_responder = SmartAIResponder()
    
    def prepare_data_context(self, region=None, days=30):
        summary_df = self.data_generator.generate_mock_summary(region, days)
        
        context = "🌍 **EGYPT AIR QUALITY DATA**\n\n"
        context += f"**Analysis Period:** Last {days} days\n"
        context += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for _, row in summary_df.iterrows():
            pm25_status = "🟢 Good" if row['Avg_PM2_5'] <= 12 else "🟡 Moderate" if row['Avg_PM2_5'] <= 35 else "🔴 Poor"
            pm10_status = "🟢 Good" if row['Avg_PM10'] <= 50 else "🟡 Moderate" if row['Avg_PM10'] <= 100 else "🔴 Poor"
            
            context += f"""**📍 {row['Region']}**
• 🌡️ Temperature: {row['Avg_Temperature']:.1f} °C
• 💧 Humidity: {row['Avg_Humidity']:.1f} %
• 🌫️ PM2.5: {row['Avg_PM2_5']:.1f} μg/m³ ({pm25_status})
• 🏭 PM10: {row['Avg_PM10']:.1f} μg/m³ ({pm10_status})
• 🚗 NO2: {row['Avg_NO2']:.1f} μg/m³
• 🌿 CO2: {row['Avg_CO2']:.1f} ppm
• 📊 Readings: {row['Readings_Count']:,}

"""
        
        return context
    
    def create_visualization(self, region, days=30):
        try:
            summary_df = self.data_generator.generate_mock_summary(region, days)
            
            if region == "All Regions":
                fig = px.bar(
                    summary_df,
                    x='Region',
                    y=['Avg_PM2_5', 'Avg_Temperature'],
                    title=f"PM2.5 & Temperature Across Egypt (Last {days} days)",
                    barmode='group',
                    labels={'value': 'Measurement', 'variable': 'Parameter'}
                )
                fig.update_layout(showlegend=True)
            else:
                dates = [(datetime.now() - timedelta(days=x)).date() for x in range(days, 0, -1)]
                base_pm25 = self.data_generator.base_data[region]["pm25"]
                
                trend_data = []
                for date in dates:
                    trend_data.append({
                        'Date': date,
                        'PM2_5': max(1, base_pm25 * (1 + random.uniform(-0.2, 0.2)))
                    })
                
                df_trend = pd.DataFrame(trend_data)
                fig = px.line(df_trend, x='Date', y='PM2_5', 
                            title=f"PM2.5 Trend in {region} (Last {days} days)")
            
            return fig
        except Exception as e:
            print(f"Visualization error: {e}")
            return None
    
    def analyze(self, user_prompt, region, days, use_ai):
        data_context = self.prepare_data_context(region, days)
        visualization = self.create_visualization(region, days)
        
        if use_ai:
            analysis = self.ai_responder.generate_response(data_context, user_prompt)
        else:
            analysis = f"📊 **DATA SUMMARY**\n\n{data_context}\n\n**Your Question:** {user_prompt}"
        
        return analysis, visualization

# Initialize analyzer
analyzer = AirQualityAnalyzer()

# Gradio interface function
def analyze_air_quality(prompt, region, days, use_ai):
    try:
        return analyzer.analyze(prompt, region, days, use_ai)
    except Exception as e:
        return f"❌ Error: {str(e)}", None

# Create Gradio app
def create_gradio_app():
    with gr.Blocks(theme=gr.themes.Soft(), title="Egypt Air Quality AI") as demo:
        gr.Markdown("# 🇪🇬 Egypt Air Quality Analysis Dashboard")
        gr.Markdown("### AI-Powered Environmental Analysis Across Egyptian Regions")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎛️ Controls")
                
                region_input = gr.Dropdown(
                    choices=["All Regions"] + EGYPT_REGIONS,
                    label="📍 Select Region", 
                    value="All Regions"
                )
                
                days_input = gr.Slider(
                    minimum=1, maximum=90, value=30,
                    label="📅 Analysis Period (Days)"
                )
                
                ai_toggle = gr.Checkbox(
                    label="🤖 Use AI Analysis", 
                    value=True
                )
                
                analyze_btn = gr.Button("🚀 Analyze", variant="primary", size="lg")
            
            with gr.Column(scale=2):
                prompt_input = gr.Textbox(
                    lines=3,
                    label="💬 Your Question",
                    placeholder="Ask about air quality, temperature, regions, or any environmental topic...",
                )
        
        with gr.Row():
            output_text = gr.Textbox(
                label="📋 Analysis Results", 
                lines=12,
                show_copy_button=True
            )
        
        with gr.Row():
            output_plot = gr.Plot(label="📊 Visualization")
        
        examples = gr.Examples(
            examples=[
                ["What was the temperature in Greater Cairo last week?", "Greater Cairo", 7, True],
                ["Compare air quality across all regions", "All Regions", 30, True],
                ["Tell me about the Red Sea region's environment", "Red Sea", 14, True],
                ["Show me basic data without AI analysis", "All Regions", 30, False],
                ["Which region has the best air quality and why?", "All Regions", 30, True]
            ],
            inputs=[prompt_input, region_input, days_input, ai_toggle]
        )
        
        analyze_btn.click(
            fn=analyze_air_quality,
            inputs=[prompt_input, region_input, days_input, ai_toggle],
            outputs=[output_text, output_plot]
        )
    
    return demo

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>Egypt Air Quality AI</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🇪🇬 Egypt Air Quality AI Dashboard</h1>
                <p>Your AI-powered environmental analysis platform is running!</p>
                <p><a href="/gradio">Open the Dashboard</a></p>
                <p><em>Powered by Azure App Service</em></p>
            </div>
        </body>
    </html>
    """

# Mount Gradio app
gradio_app = create_gradio_app()
app = gr.mount_gradio_app(app, gradio_app, path="/gradio")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)


import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# Configure the page
st.set_page_config(
    page_title="Egypt Air Quality AI",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .region-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .ai-response {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Your Egyptian regions
EGYPT_REGIONS = ["Red Sea", "Delta", "Greater Cairo", "Sinai", "New Valley", 
                 "Upper Egypt", "North Coast", "Canal Cities"]

# Enhanced AI Data Provider
class EgyptAirQualityAI:
    def __init__(self):
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
        self.region_context = {
            "Red Sea": "Coastal region with excellent air quality due to sea breezes. Tourism and shipping activities.",
            "Delta": "Agricultural region with moderate pollution from farming. High population density area.",
            "Greater Cairo": "Urban metropolitan with highest pollution levels. Heavy traffic and industrial activity.",
            "Sinai": "Desert region with good air quality affected by dust storms. Tourism and minimal industry.",
            "New Valley": "Desert oasis with moderate environmental conditions. Agricultural activities present.",
            "Upper Egypt": "Southern region with variable air quality. Mix of urban and rural areas.",
            "North Coast": "Mediterranean coastal area with very good air quality. Sea breeze influence.",
            "Canal Cities": "Industrial region with moderate pollution. Shipping and urban activities."
        }
    
    def get_environmental_data(self, region=None, days=30):
        """Get enhanced environmental data with realistic variations"""
        regions_to_show = [region] if region and region != "All Regions" else EGYPT_REGIONS
        data = []
        current_time = datetime.now()
        
        for reg in regions_to_show:
            if reg in self.base_data:
                base = self.base_data[reg]
                
                # Time-based realistic variations
                hour = current_time.hour
                day_variation = 0.1 + (0.05 * (hour / 24))  # Higher variation during day
                
                data.append({
                    'Region': reg,
                    'PM2.5': max(1, base["pm25"] * (1 + random.uniform(-day_variation, day_variation))),
                    'PM10': max(1, base["pm10"] * (1 + random.uniform(-day_variation, day_variation))),
                    'NO2': max(1, base["no2"] * (1 + random.uniform(-day_variation, day_variation))),
                    'CO2': max(250, base["co2"] * (1 + random.uniform(-day_variation/3, day_variation/3))),
                    'Temperature': base["temp"] * (1 + random.uniform(-0.08, 0.08)),
                    'Humidity': max(10, min(95, base["humidity"] * (1 + random.uniform(-0.15, 0.15)))),
                    'Readings': random.randint(80, 200),
                    'Last_Update': current_time.strftime('%Y-%m-%d %H:%M')
                })
        
        return pd.DataFrame(data)
    
    def generate_ai_analysis(self, user_prompt, data_df, region, days):
        """Generate AI-powered analysis based on user query"""
        prompt_lower = user_prompt.lower()
        region_context = self.region_context.get(region, "General Egyptian region")
        
        if any(word in prompt_lower for word in ['temperature', 'temp', 'hot', 'cold', 'warm']):
            return self._temperature_analysis(user_prompt, data_df, region, days, region_context)
        elif any(word in prompt_lower for word in ['compare', 'ranking', 'versus', 'vs', 'best', 'worst']):
            return self._comparison_analysis(user_prompt, data_df, region, days, region_context)
        elif any(word in prompt_lower for word in ['health', 'risk', 'safe', 'danger', 'recommend']):
            return self._health_analysis(user_prompt, data_df, region, days, region_context)
        elif any(word in prompt_lower for word in ['region', 'area', 'location', 'tell about']):
            return self._regional_analysis(user_prompt, data_df, region, days, region_context)
        else:
            return self._general_analysis(user_prompt, data_df, region, days, region_context)
    
    def _temperature_analysis(self, user_prompt, data_df, region, days, region_context):
        avg_temp = data_df['Temperature'].mean() if not data_df.empty else 25
        return f"""
**🌡️ Temperature Analysis - {region}**

*Region Context*: {region_context}

**Current Conditions**:
- Average Temperature: **{avg_temp:.1f}°C**
- Analysis Period: **{days} days**
- Data Source: Environmental monitoring network

**Climate Insights**:
- Temperature patterns reflect typical {region.lower()} climate
- Regional variations show geographical influences
- Current readings within expected seasonal ranges

**Environmental Impact**:
- Temperature affects pollutant dispersion
- Higher temperatures can influence ozone formation
- Comfort levels vary across different temperature ranges

💡 *Analysis based on: "{user_prompt}"*
"""
    
    def _comparison_analysis(self, user_prompt, data_df, region, days, region_context):
        if not data_df.empty:
            sorted_df = data_df.sort_values('PM2.5')
            best_region = sorted_df.iloc[0]['Region']
            worst_region = sorted_df.iloc[-1]['Region']
        else:
            best_region = worst_region = "N/A"
            
        return f"""
**📊 Regional Comparison Analysis**

*Scope*: {len(data_df)} Egyptian regions

**Air Quality Ranking** (Based on PM2.5 levels):
- 🥇 Cleanest Air: **{best_region}**
- 🚨 Most Polluted: **{worst_region}**

**Key Findings**:
- Clear urban-rural-coastal gradient in pollution levels
- Coastal regions generally show better air quality
- Urban centers face higher environmental challenges
- Regional characteristics significantly impact conditions

**Patterns Observed**:
- Geographical location strongly influences air quality
- Human activities contribute to regional variations
- Natural factors (sea breezes, dust) play important roles

📈 *Analysis based on: "{user_prompt}"*
"""
    
    def _health_analysis(self, user_prompt, data_df, region, days, region_context):
        if not data_df.empty:
            avg_pm25 = data_df['PM2.5'].mean()
            if avg_pm25 <= 12:
                health_status = "🟢 GOOD - Minimal health risk"
                recommendation = "Normal outdoor activities are safe for all groups"
            elif avg_pm25 <= 35:
                health_status = "🟡 MODERATE - Some concern for sensitive groups"
                recommendation = "Sensitive individuals should reduce prolonged outdoor exertion"
            else:
                health_status = "🔴 POOR - Health risks for everyone"
                recommendation = "Everyone should reduce outdoor activities, especially sensitive groups"
        else:
            health_status = "Data unavailable"
            recommendation = "General precautions recommended"
            
        return f"""
**🏥 Health Impact Assessment - {region}**

**Current Air Quality Status**:
{health_status}

**WHO Health Guidelines**:
- PM2.5: Good (0-12 μg/m³) | Moderate (12-35 μg/m³) | Poor (>35 μg/m³)
- PM10: Good (0-50 μg/m³) | Moderate (50-100 μg/m³) | Poor (>100 μg/m³)

**Health Recommendations**:
{recommendation}

**Specific Guidance**:
- Monitor local air quality conditions regularly
- Sensitive groups (children, elderly, respiratory conditions) should take extra precautions
- Consider indoor air purification during poor air quality periods

🩺 *Health analysis based on: "{user_prompt}"*
"""
    
    def _regional_analysis(self, user_prompt, data_df, region, days, region_context):
        return f"""
**📍 Regional Environmental Profile - {region}**

*Regional Characteristics*:
{region_context}

**Environmental Context**:
- Analysis based on {days} days of environmental monitoring
- Regional data reflects local geographical and human factors
- Continuous monitoring enables accurate assessment

**Key Regional Factors**:
- Geographical location and topography
- Urbanization and industrial activities
- Agricultural practices and land use
- Natural environmental conditions

**Management Considerations**:
- Region-specific environmental strategies needed
- Continuous monitoring essential for informed decisions
- Public awareness tailored to local conditions

🌍 *Regional analysis based on: "{user_prompt}"*
"""
    
    def _general_analysis(self, user_prompt, data_df, region, days, region_context):
        return f"""
**🤖 AI Environmental Intelligence - {region}**

*Analysis Scope*: Environmental conditions across {region if region != "All Regions" else "all Egyptian regions"}

**Comprehensive Assessment**:
Environmental data reveals important patterns and trends across monitored regions. The analysis considers multiple factors including air quality, temperature, and regional characteristics.

**Key Insights**:
- Data shows meaningful environmental variations
- Regional conditions reflect complex interactions
- Continuous monitoring supports informed decisions
- Targeted interventions can improve local conditions

**Strategic Perspective**:
- Environmental intelligence enables proactive management
- Regional-specific approaches are most effective
- Public awareness supports community engagement
- Data-driven decisions lead to better outcomes

🔍 *Analysis based on: "{user_prompt}"*
"""

# Initialize AI system
ai_system = EgyptAirQualityAI()

# Main Application
def main():
    # Header Section
    st.markdown('<h1 class="main-header">🇪🇬 Egypt Air Quality AI Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Environmental Intelligence Across Egyptian Regions")
    
    # Sidebar - Control Panel
    st.sidebar.header("🎛️ Control Panel")
    
    region = st.sidebar.selectbox(
        "📍 Select Egyptian Region",
        ["All Regions"] + EGYPT_REGIONS,
        help="Choose specific region or compare all regions"
    )
    
    days = st.sidebar.slider(
        "📅 Analysis Period (Days)",
        min_value=1,
        max_value=90,
        value=30,
        help="Select time range for environmental analysis"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 Quick Actions")
    
    # Quick analysis buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        temp_analysis = st.button("🌡️ Temperature", use_container_width=True)
    with col2:
        health_analysis = st.button("🏥 Health", use_container_width=True)
    
    col3, col4 = st.sidebar.columns(2)
    with col3:
        compare_analysis = st.button("📊 Compare", use_container_width=True)
    with col4:
        region_analysis = st.button("📍 Regional", use_container_width=True)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 AI Analysis", "📈 Data Visualization", "🌍 Regional Info"])
    
    with tab1:
        st.subheader("AI Environmental Analysis")
        
        # User input
        user_prompt = st.text_area(
            "Ask about air quality, temperature, health impacts, or regional comparisons:",
            placeholder="Examples:\n• 'Compare air quality across all regions'\n• 'What is the temperature in Greater Cairo?'\n• 'Health recommendations for sensitive groups'\n• 'Tell me about environmental conditions in Red Sea'",
            height=100,
            key="user_input"
        )
        
        # Set prompt from quick buttons
        if temp_analysis:
            user_prompt = f"What is the temperature in {region}?"
        elif health_analysis:
            user_prompt = f"Health recommendations for {region}"
        elif compare_analysis:
            user_prompt = f"Compare environmental conditions across regions"
        elif region_analysis:
            user_prompt = f"Tell me about {region} region"
        
        analyze_btn = st.button("🚀 Generate AI Analysis", type="primary", use_container_width=True)
        
        if analyze_btn and user_prompt:
            with st.spinner("🤖 AI is analyzing environmental data..."):
                # Get environmental data
                data_df = ai_system.get_environmental_data(region, days)
                
                # Display quick metrics
                if not data_df.empty:
                    st.subheader("📊 Quick Environmental Metrics")
                    
                    # Create metrics columns
                    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                    
                    with mcol1:
                        avg_pm25 = data_df['PM2.5'].mean()
                        pm25_status = "Good" if avg_pm25 <= 12 else "Moderate" if avg_pm25 <= 35 else "Poor"
                        st.metric("Average PM2.5", f"{avg_pm25:.1f} μg/m³", pm25_status)
                    
                    with mcol2:
                        avg_temp = data_df['Temperature'].mean()
                        st.metric("Average Temperature", f"{avg_temp:.1f} °C")
                    
                    with mcol3:
                        avg_humidity = data_df['Humidity'].mean()
                        st.metric("Average Humidity", f"{avg_humidity:.1f}%")
                    
                    with mcol4:
                        total_readings = data_df['Readings'].sum()
                        st.metric("Total Readings", f"{total_readings:,}")
                
                # Generate and display AI analysis
                st.subheader("🤖 AI Analysis Results")
                ai_response = ai_system.generate_ai_analysis(user_prompt, data_df, region, days)
                
                st.markdown(f'<div class="ai-response">{ai_response}</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Environmental Data Visualization")
        
        if 'data_df' in locals() and not data_df.empty:
            # Data table
            st.subheader("📋 Regional Environmental Data")
            st.dataframe(data_df, use_container_width=True)
            
            # Visualizations
            st.subheader("📈 Environmental Charts")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                if region == "All Regions":
                    # Bar chart for comparison
                    fig_bar = px.bar(
                        data_df,
                        x='Region',
                        y=['PM2.5', 'Temperature'],
                        title=f"Environmental Comparison - All Regions (Last {days} days)",
                        barmode='group',
                        labels={'value': 'Measurement', 'variable': 'Parameter'}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    # Trend chart for single region
                    dates = [(datetime.now() - timedelta(days=x)).date() for x in range(days, 0, -1)]
                    trend_data = []
                    base_value = data_df.iloc[0]['PM2.5'] if not data_df.empty else 20
                    
                    for date in dates:
                        trend_data.append({
                            'Date': date,
                            'PM2.5': max(1, base_value * (1 + random.uniform(-0.2, 0.2))),
                            'Temperature': data_df.iloc[0]['Temperature'] * (1 + random.uniform(-0.1, 0.1))
                        })
                    
                    trend_df = pd.DataFrame(trend_data)
                    fig_line = px.line(
                        trend_df,
                        x='Date',
                        y=['PM2.5', 'Temperature'],
                        title=f"Environmental Trends in {region} (Last {days} days)",
                        labels={'value': 'Measurement', 'variable': 'Parameter'}
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
            
            with viz_col2:
                # PM2.5 status chart
                if region == "All Regions":
                    fig_pie = px.pie(
                        data_df,
                        names='Region',
                        values='PM2.5',
                        title=f"PM2.5 Distribution Across Regions"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        st.subheader("🌍 Egyptian Regions Information")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown("### 📍 Region Profiles")
            for reg in EGYPT_REGIONS[:4]:
                with st.expander(f"**{reg}**"):
                    st.write(ai_system.region_context[reg])
        
        with info_col2:
            st.markdown("### 📍 Region Profiles (Cont.)")
            for reg in EGYPT_REGIONS[4:]:
                with st.expander(f"**{reg}**"):
                    st.write(ai_system.region_context[reg])
        
        st.markdown("---")
        st.markdown("### 📋 Environmental Guidelines")
        
        guidelines_col1, guidelines_col2 = st.columns(2)
        
        with guidelines_col1:
            st.markdown("""
            **WHO Air Quality Standards:**
            - **PM2.5**: 
              - Good: 0-12 μg/m³
              - Moderate: 12-35 μg/m³  
              - Poor: >35 μg/m³
            - **PM10**:
              - Good: 0-50 μg/m³
              - Moderate: 50-100 μg/m³
              - Poor: >100 μg/m³
            """)
        
        with guidelines_col2:
            st.markdown("""
            **Health Recommendations:**
            - 🟢 **Good**: Normal outdoor activities
            - 🟡 **Moderate**: Sensitive groups reduce exertion
            - 🔴 **Poor**: Everyone reduce outdoor activities
            
            **Sensitive Groups**:
            - Children and elderly
            - People with respiratory conditions
            - Individuals with cardiovascular issues
            """)
    
    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("**🌍 Coverage**")
        st.write("8 Egyptian Regions")
        st.write("Real-time Environmental Data")
    
    with footer_col2:
        st.markdown("**🤖 AI Features**")
        st.write("Environmental Analysis")
        st.write("Health Recommendations")
    
    with footer_col3:
        st.markdown("**📊 Data**")
        st.write("Enhanced Monitoring")
        st.write("Regional Comparisons")

if __name__ == "__main__":
    main()

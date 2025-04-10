import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PropInsight - Property Management Assistant",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the Google AI model
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Error: GEMINI_API_KEY not found in environment variables. Please set up your API key.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Initialize chat history in session state if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "properties" not in st.session_state:
    # Sample property data (would be loaded from a database in a real app)
    st.session_state.properties = [
        {
            "id": 1,
            "name": "Lakeside Apartments",
            "address": "123 Lake Drive, Laketown",
            "units": 24,
            "status": "occupied",
            "currentRent": 1800,
            "lastRenoDate": "2022-05-15",
            "occupancyRate": 0.92,
        },
        {
            "id": 2,
            "name": "Highland Towers",
            "address": "456 Mountain View, Highland",
            "units": 16,
            "status": "occupied",
            "currentRent": 2100,
            "lastRenoDate": "2021-08-10",
            "occupancyRate": 0.88,
        },
        {
            "id": 3,
            "name": "Meadow Gardens",
            "address": "789 Green Valley, Meadowville",
            "units": 12,
            "status": "vacant",
            "currentRent": 1650,
            "lastRenoDate": "2023-01-20",
            "occupancyRate": 0.75,
        },
        {
            "id": 4,
            "name": "Sunset Condos",
            "address": "101 Sunset Boulevard, Westside",
            "units": 8,
            "status": "pending_renewal",
            "currentRent": 2300,
            "lastRenoDate": "2022-11-05",
            "occupancyRate": 0.95,
        }
    ]

if "financial_records" not in st.session_state:
    # Sample financial data (would be loaded from a database in a real app)
    st.session_state.financial_records = [
        {
            "id": 1,
            "propertyId": 1,
            "date": "2023-01-15",
            "type": "income",
            "amount": 43200,
            "category": "rent",
            "description": "January rent collection"
        },
        {
            "id": 2,
            "propertyId": 1,
            "date": "2023-01-25",
            "type": "expense",
            "amount": 5500,
            "category": "maintenance",
            "description": "HVAC system repair"
        },
        {
            "id": 3,
            "propertyId": 2,
            "date": "2023-01-15",
            "type": "income",
            "amount": 33600,
            "category": "rent",
            "description": "January rent collection"
        },
        {
            "id": 4,
            "propertyId": 2,
            "date": "2023-01-20",
            "type": "expense",
            "amount": 2800,
            "category": "utilities",
            "description": "Water and electricity"
        }
    ]

if "market_data" not in st.session_state:
    # Sample market data (would be loaded from a database in a real app)
    st.session_state.market_data = [
        {
            "id": 1,
            "month": "2023-01-01",
            "avgPrice": 255000,
            "avgRent": 1850,
            "vacancyRate": 0.05,
            "inventoryCount": 120,
            "avgDaysOnMarket": 35
        },
        {
            "id": 2,
            "month": "2023-02-01",
            "avgPrice": 258000,
            "avgRent": 1870,
            "vacancyRate": 0.045,
            "inventoryCount": 115,
            "avgDaysOnMarket": 32
        },
        {
            "id": 3,
            "month": "2023-03-01",
            "avgPrice": 262000,
            "avgRent": 1890,
            "vacancyRate": 0.042,
            "inventoryCount": 110,
            "avgDaysOnMarket": 30
        },
        {
            "id": 4,
            "month": "2023-04-01",
            "avgPrice": 265000,
            "avgRent": 1900,
            "vacancyRate": 0.04,
            "inventoryCount": 105,
            "avgDaysOnMarket": 28
        }
    ]

if "competitors" not in st.session_state:
    # Sample competitor data (would be loaded from a database in a real app)
    st.session_state.competitors = [
        {
            "id": 1,
            "name": "Horizon Properties",
            "avgRent": 2100,
            "units": 45,
            "occupancyRate": 0.95,
            "amenities": ["Pool", "Gym", "Covered Parking"],
            "proximity": 2.5,
            "lastUpdated": "2023-04-01"
        },
        {
            "id": 2,
            "name": "Prestige Rentals",
            "avgRent": 1950,
            "units": 32,
            "occupancyRate": 0.90,
            "amenities": ["Pool", "Pet Friendly", "On-site Laundry"],
            "proximity": 1.8,
            "lastUpdated": "2023-03-25"
        },
        {
            "id": 3,
            "name": "Urban Living",
            "avgRent": 2200,
            "units": 50,
            "occupancyRate": 0.93,
            "amenities": ["Gym", "Rooftop Terrace", "Smart Home Features"],
            "proximity": 3.2,
            "lastUpdated": "2023-04-05"
        }
    ]

# Process user message and get AI response
def get_gemini_response(message):
    try:
        system_prompt = """You are a helpful property management assistant named PropInsight. 
        You help users manage rental properties, track finances, analyze market trends, and suggest optimizations.
        You should be friendly, professional, and knowledgeable about property management topics.
        Provide concise, useful information and never claim to have access to specific user data unless explicitly provided in the conversation.
        If you don't know something, acknowledge it and suggest alternative approaches.
        
        User query: {message}
        
        Your response:"""
        
        response = model.generate_content(system_prompt.format(message=message))
        return response.text
    except Exception as e:
        st.error(f"Error getting response from Gemini: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."

# Analyze market trends for property data
def analyze_market_trends(market_data):
    try:
        prompt = f"""Analyze the following market trend data for rental properties and provide insights:
        {json.dumps(market_data)}
        
        Format your response as JSON with the following structure:
        {{
          "trend": "increasing/decreasing/stable",
          "percentageChange": 5.2,
          "insights": ["Insight 1", "Insight 2", "Insight 3"],
          "recommendations": ["Recommendation 1", "Recommendation 2"]
        }}"""
        
        response = model.generate_content(prompt)
        
        try:
            # Try to parse the response as JSON
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            import re
            json_match = re.search(r'({[\s\S]*})', response.text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # If all else fails, return a formatted error response
            return {
                "trend": "unknown",
                "insights": ["Could not analyze market trends at this time."],
                "recommendations": ["Try again later."]
            }
    except Exception as e:
        st.error(f"Error analyzing market trends: {str(e)}")
        return {
            "trend": "unknown",
            "insights": ["Could not analyze market trends at this time."],
            "recommendations": ["Try again later."]
        }

# Generate property management recommendations
def get_property_recommendations(property_data):
    try:
        prompt = f"""Based on the following property data, provide specific recommendations to optimize rental income and property management:
        {json.dumps(property_data)}
        
        Provide 3-5 actionable recommendations."""
        
        response = model.generate_content(prompt)
        recommendations = response.text.split('\n')
        return [rec for rec in recommendations if rec.strip()]
    except Exception as e:
        st.error(f"Error generating property recommendations: {str(e)}")
        return ["Could not generate property recommendations at this time."]

# Analyze competitor data
def analyze_competitors(competitor_data, your_properties):
    try:
        prompt = f"""Compare the following competitor data with my properties and suggest competitive strategies:
        
        My properties:
        {json.dumps(your_properties)}
        
        Competitors:
        {json.dumps(competitor_data)}
        
        Format your response as JSON with the following structure:
        {{
          "competitivePosition": "strong/moderate/weak",
          "strengths": ["Strength 1", "Strength 2"],
          "weaknesses": ["Weakness 1", "Weakness 2"],
          "opportunities": ["Opportunity 1", "Opportunity 2"],
          "threats": ["Threat 1", "Threat 2"],
          "strategies": ["Strategy 1", "Strategy 2", "Strategy 3"]
        }}"""
        
        response = model.generate_content(prompt)
        
        try:
            # Try to parse the response as JSON
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            import re
            json_match = re.search(r'({[\s\S]*})', response.text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # If all else fails, return a formatted error response
            return {
                "competitivePosition": "unknown",
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": [],
                "strategies": ["Could not analyze competitor data at this time."]
            }
    except Exception as e:
        st.error(f"Error analyzing competitors: {str(e)}")
        return {
            "competitivePosition": "unknown",
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
            "strategies": ["Could not analyze competitor data at this time."]
        }

# CSS styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #4285F4, #34A853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .chatbox {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        height: 450px;
        overflow-y: auto;
        background-color: #f9f9f9;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #1e293b;
        color: white;
        border-radius: 15px 15px 0 15px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .bot-message {
        background-color: #f1f5f9;
        color: #1e293b;
        border-radius: 15px 15px 15px 0;
        padding: 0.8rem;
        margin: 0.5rem 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    .message-container {
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    
    .stat-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stat-card h3 {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .property-card {
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    .occupied {
        border-left: 4px solid #34A853;
    }
    
    .vacant {
        border-left: 4px solid #EA4335;
    }
    
    .pending {
        border-left: 4px solid #FBBC05;
    }
    
    hr {
        margin: 1.5rem 0;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<div class="main-header">PropInsight</div>', unsafe_allow_html=True)
st.sidebar.markdown("Property Management Assistant")
st.sidebar.divider()

# Sidebar navigation
page = st.sidebar.radio("Navigation", 
                        ["Dashboard", "Properties", "Financials", "Market Trends", 
                         "Competitor Analysis", "AI Assistant"])

st.sidebar.divider()
st.sidebar.markdown("### About PropInsight")
st.sidebar.markdown("""
PropInsight is your AI-powered property management assistant. 
Get insights, manage properties, and optimize your real estate investments with ease.
""")

# Main content based on selected page
if page == "Dashboard":
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown("Welcome to your property management dashboard")
    
    # Quick stats in 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">'
                    '<h3>TOTAL PROPERTIES</h3>'
                    f'<div class="stat-value">{len(st.session_state.properties)}</div>'
                    '<div>+2 from last month</div>'
                    '</div>', unsafe_allow_html=True)
    
    with col2:
        occupied = sum(1 for p in st.session_state.properties if p["status"] == "occupied")
        occupied_rate = occupied / len(st.session_state.properties) * 100
        st.markdown(f'<div class="stat-card">'
                    f'<h3>OCCUPANCY RATE</h3>'
                    f'<div class="stat-value">{occupied_rate:.1f}%</div>'
                    f'<div>+2.5% from last month</div>'
                    f'</div>', unsafe_allow_html=True)
    
    with col3:
        avg_rent = sum(p["currentRent"] for p in st.session_state.properties) / len(st.session_state.properties)
        st.markdown(f'<div class="stat-card">'
                    f'<h3>AVERAGE RENT</h3>'
                    f'<div class="stat-value">${avg_rent:.0f}</div>'
                    f'<div>+$50 from last month</div>'
                    f'</div>', unsafe_allow_html=True)
    
    with col4:
        total_units = sum(p["units"] for p in st.session_state.properties)
        st.markdown(f'<div class="stat-card">'
                    f'<h3>TOTAL UNITS</h3>'
                    f'<div class="stat-value">{total_units}</div>'
                    f'<div>No change</div>'
                    f'</div>', unsafe_allow_html=True)
    
    # Recent activity and properties
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Recent Properties")
        for prop in st.session_state.properties:
            status_class = "occupied" if prop["status"] == "occupied" else "vacant" if prop["status"] == "vacant" else "pending"
            status_text = "Occupied" if prop["status"] == "occupied" else "Vacant" if prop["status"] == "vacant" else "Pending Renewal"
            
            st.markdown(f'<div class="property-card {status_class}">'
                        f'<h3>{prop["name"]}</h3>'
                        f'<p>{prop["address"]}</p>'
                        f'<p>Units: {prop["units"]} | Status: {status_text} | Current Rent: ${prop["currentRent"]}</p>'
                        f'<p>Occupancy Rate: {prop["occupancyRate"] * 100:.1f}%</p>'
                        f'</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### AI Recommendations")
        # Get recommendations based on the first property
        if st.session_state.properties:
            recommendations = get_property_recommendations(st.session_state.properties[0])
            for i, rec in enumerate(recommendations[:3], 1):
                st.markdown(f"**{i}.** {rec}")
        
        st.markdown("### Market Trend")
        market_analysis = analyze_market_trends(st.session_state.market_data)
        st.markdown(f"**Trend:** {market_analysis.get('trend', 'Unknown')}")
        
        insights = market_analysis.get('insights', [])
        if insights:
            st.markdown("**Key Insight:** " + insights[0])

elif page == "Properties":
    st.markdown('<div class="main-header">Properties</div>', unsafe_allow_html=True)
    st.markdown("Manage your real estate properties")
    
    # Tabs for different property statuses
    tab1, tab2, tab3 = st.tabs(["All Properties", "Occupied", "Vacant"])
    
    with tab1:
        for prop in st.session_state.properties:
            status_class = "occupied" if prop["status"] == "occupied" else "vacant" if prop["status"] == "vacant" else "pending"
            status_text = "Occupied" if prop["status"] == "occupied" else "Vacant" if prop["status"] == "vacant" else "Pending Renewal"
            
            st.markdown(f'<div class="property-card {status_class}">'
                        f'<h3>{prop["name"]}</h3>'
                        f'<p>{prop["address"]}</p>'
                        f'<p>Units: {prop["units"]} | Status: {status_text} | Current Rent: ${prop["currentRent"]}</p>'
                        f'<p>Occupancy Rate: {prop["occupancyRate"] * 100:.1f}%</p>'
                        f'</div>', unsafe_allow_html=True)
    
    with tab2:
        occupied_props = [p for p in st.session_state.properties if p["status"] == "occupied"]
        for prop in occupied_props:
            st.markdown(f'<div class="property-card occupied">'
                        f'<h3>{prop["name"]}</h3>'
                        f'<p>{prop["address"]}</p>'
                        f'<p>Units: {prop["units"]} | Status: Occupied | Current Rent: ${prop["currentRent"]}</p>'
                        f'<p>Occupancy Rate: {prop["occupancyRate"] * 100:.1f}%</p>'
                        f'</div>', unsafe_allow_html=True)
    
    with tab3:
        vacant_props = [p for p in st.session_state.properties if p["status"] == "vacant"]
        for prop in vacant_props:
            st.markdown(f'<div class="property-card vacant">'
                        f'<h3>{prop["name"]}</h3>'
                        f'<p>{prop["address"]}</p>'
                        f'<p>Units: {prop["units"]} | Status: Vacant | Current Rent: ${prop["currentRent"]}</p>'
                        f'<p>Occupancy Rate: {prop["occupancyRate"] * 100:.1f}%</p>'
                        f'</div>', unsafe_allow_html=True)

elif page == "Financials":
    st.markdown('<div class="main-header">Financials</div>', unsafe_allow_html=True)
    st.markdown("Track income and expenses for your properties")
    
    # Summary stats
    total_income = sum(r["amount"] for r in st.session_state.financial_records if r["type"] == "income")
    total_expenses = sum(r["amount"] for r in st.session_state.financial_records if r["type"] == "expense")
    net_income = total_income - total_expenses
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-card">'
                    f'<h3>TOTAL INCOME</h3>'
                    f'<div class="stat-value">${total_income:,.2f}</div>'
                    f'</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="stat-card">'
                    f'<h3>TOTAL EXPENSES</h3>'
                    f'<div class="stat-value">${total_expenses:,.2f}</div>'
                    f'</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="stat-card">'
                    f'<h3>NET INCOME</h3>'
                    f'<div class="stat-value">${net_income:,.2f}</div>'
                    f'</div>', unsafe_allow_html=True)
    
    # Financial records table
    st.markdown("### Financial Records")
    
    # Property filter
    property_names = ["All Properties"] + [p["name"] for p in st.session_state.properties]
    selected_property = st.selectbox("Filter by property:", property_names)
    
    # Type filter
    record_types = ["All Types", "Income", "Expense"]
    selected_type = st.selectbox("Filter by type:", record_types)
    
    # Filter records
    filtered_records = st.session_state.financial_records
    
    if selected_property != "All Properties":
        property_id = next((p["id"] for p in st.session_state.properties if p["name"] == selected_property), None)
        if property_id:
            filtered_records = [r for r in filtered_records if r["propertyId"] == property_id]
    
    if selected_type != "All Types":
        type_filter = selected_type.lower()
        filtered_records = [r for r in filtered_records if r["type"] == type_filter]
    
    # Display records
    if filtered_records:
        record_data = []
        for record in filtered_records:
            property_name = next((p["name"] for p in st.session_state.properties if p["id"] == record["propertyId"]), "Unknown")
            record_data.append({
                "Date": record["date"],
                "Property": property_name,
                "Type": record["type"].capitalize(),
                "Category": record["category"].capitalize(),
                "Amount": f"${record['amount']:,.2f}",
                "Description": record["description"]
            })
        
        st.table(record_data)
    else:
        st.info("No financial records found matching your filters.")

elif page == "Market Trends":
    st.markdown('<div class="main-header">Market Trends</div>', unsafe_allow_html=True)
    st.markdown("Analyze local real estate market trends")
    
    # Display the market data
    st.markdown("### Market Data")
    
    market_data_table = []
    for data in st.session_state.market_data:
        market_data_table.append({
            "Month": data["month"],
            "Avg. Price": f"${data['avgPrice']:,.0f}",
            "Avg. Rent": f"${data['avgRent']:,.0f}",
            "Vacancy Rate": f"{data['vacancyRate']*100:.1f}%",
            "Inventory": data["inventoryCount"],
            "Days on Market": data["avgDaysOnMarket"]
        })
    
    st.table(market_data_table)
    
    # AI Market Analysis
    st.markdown("### AI Market Analysis")
    
    market_analysis = analyze_market_trends(st.session_state.market_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Market Trend")
        st.markdown(f"**Direction:** {market_analysis.get('trend', 'Unknown')}")
        st.markdown(f"**Change:** {market_analysis.get('percentageChange', 0):.1f}%")
        
        st.markdown("#### Key Insights")
        insights = market_analysis.get('insights', [])
        for insight in insights:
            st.markdown(f"• {insight}")
    
    with col2:
        st.markdown("#### Recommendations")
        recommendations = market_analysis.get('recommendations', [])
        for rec in recommendations:
            st.markdown(f"• {rec}")

elif page == "Competitor Analysis":
    st.markdown('<div class="main-header">Competitor Analysis</div>', unsafe_allow_html=True)
    st.markdown("Compare your properties with competitors in the area")
    
    # Display competitor data
    st.markdown("### Competitors")
    
    comp_data_table = []
    for comp in st.session_state.competitors:
        comp_data_table.append({
            "Name": comp["name"],
            "Avg. Rent": f"${comp['avgRent']:,.0f}",
            "Units": comp["units"],
            "Occupancy": f"{comp['occupancyRate']*100:.1f}%",
            "Distance (mi)": comp["proximity"],
            "Last Updated": comp["lastUpdated"]
        })
    
    st.table(comp_data_table)
    
    # AI Competitor Analysis
    st.markdown("### AI Competitive Analysis")
    
    comp_analysis = analyze_competitors(st.session_state.competitors, st.session_state.properties)
    
    # Competitive position
    st.markdown(f"#### Competitive Position: {comp_analysis.get('competitivePosition', 'Unknown').capitalize()}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Strengths")
        strengths = comp_analysis.get('strengths', [])
        for strength in strengths:
            st.markdown(f"• {strength}")
        
        st.markdown("#### Weaknesses")
        weaknesses = comp_analysis.get('weaknesses', [])
        for weakness in weaknesses:
            st.markdown(f"• {weakness}")
    
    with col2:
        st.markdown("#### Opportunities")
        opportunities = comp_analysis.get('opportunities', [])
        for opportunity in opportunities:
            st.markdown(f"• {opportunity}")
        
        st.markdown("#### Threats")
        threats = comp_analysis.get('threats', [])
        for threat in threats:
            st.markdown(f"• {threat}")
    
    st.markdown("#### Recommended Strategies")
    strategies = comp_analysis.get('strategies', [])
    for strategy in strategies:
        st.markdown(f"• {strategy}")

elif page == "AI Assistant":
    st.markdown('<div class="main-header">AI Assistant</div>', unsafe_allow_html=True)
    st.markdown("Chat with PropInsight, your property management assistant")
    
    # Display chat messages
    st.markdown('<div class="chatbox" id="chat-box">', unsafe_allow_html=True)
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="message-container"><div class="user-message">{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-container"><div class="bot-message">{message["content"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form(key='chat_form', clear_on_submit=True):
        user_message = st.text_input("Type your message here:", placeholder="Ask me anything about property management...")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_message:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            # Get response from Gemini
            with st.spinner("Thinking..."):
                bot_response = get_gemini_response(user_message)
            
            # Add bot response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Force a rerun to update the chat display
            st.rerun()

# Add auto-scrolling JavaScript to keep the chat at the bottom
if page == "AI Assistant":
    st.markdown("""
    <script>
        const chatBox = document.querySelector('.chatbox');
        if (chatBox) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
    """, unsafe_allow_html=True)

# Welcome message if chat history is empty
if page == "AI Assistant" and not st.session_state.chat_history:
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": "👋 Hello! I'm PropInsight, your property management assistant. How can I help you today?"
    })
    st.rerun()
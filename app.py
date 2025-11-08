import streamlit as st
import pandas as pd
import numpy as np
import pickle
import joblib
import warnings
from datetime import datetime
from ui import load_custom_ui  
import time
import numpy_financial as npf
import os
import traceback


# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Investment Decision Predictor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load UI (apply auto theme and a dynamic title)
app_title = "Capital Investment Model"
load_custom_ui(theme="auto", title=app_title)

# --- Header and Role Selection Section ---
st.markdown("""
<div class="header-container">
    <div class="role-selection-card">
        <div class="role-selection-header">
            <h2>Choose Your Role</h2>
            <p>Select whether you're an investor looking to analyze opportunities or a company seeking investment guidance</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- App state: role selection ---
col1, col2 = st.columns(2)
with col1:
    investor_selected = st.button(
        "📊 Investor", 
        key="investor_btn",
        help="Analyze investment opportunities",
        use_container_width=True
    )
with col2:
    company_selected = st.button(
        "🏢 Company", 
        key="company_btn",
        help="Get investment suggestions",
        use_container_width=True
    )

# Set role based on button clicks
if 'role' not in st.session_state:
    st.session_state.role = "Investor"

if investor_selected:
    st.session_state.role = "Investor"
elif company_selected:
    st.session_state.role = "Company"

role = st.session_state.role


# --- Investor models loader (original functionality) ---
@st.cache_resource
def load_investor_models():
    try:
        with open('models/cash_flow_regressor.pkl', 'rb') as file:
            regressor_model = pickle.load(file)
        classifier_model = joblib.load('models/decision_classifier.pkl')
        return regressor_model, classifier_model
    except FileNotFoundError:
        return None, None
    except Exception:
        return None, None

regressor_model, classifier_model = load_investor_models()

# --- Financial Metrics Function ---
def calculate_financial_metrics(initial_cost, discount_rate, cash_flows):
    """Calculate NPV, IRR, PI, and Payback Period with error handling"""
    try:
        cash_flows = np.array(cash_flows)
        npv = np.sum(cash_flows / (1 + discount_rate/100) ** np.arange(1, len(cash_flows) + 1)) - abs(initial_cost)
        try:
            all_cash_flows = np.concatenate([[initial_cost], cash_flows])
            irr = npf.irr(all_cash_flows) * 100
        except:
            irr = (np.sum(cash_flows) / abs(initial_cost) - 1) * 100 / len(cash_flows)
        pi = (npv + abs(initial_cost)) / abs(initial_cost) if initial_cost != 0 else 0

        cumulative_cf = 0
        payback_period = None
        for i, cf in enumerate(cash_flows, 1):
            cumulative_cf += cf
            if cumulative_cf >= abs(initial_cost):
                if i > 1:
                    prev_cumulative = cumulative_cf - cf
                    remaining = abs(initial_cost) - prev_cumulative
                    fraction = remaining / cf if cf != 0 else 0
                    payback_period = i - 1 + fraction
                else:
                    payback_period = i
                break
        if payback_period is None:
            payback_period = len(cash_flows)
        return npv, irr, pi, payback_period
    except Exception as e:
        st.error(f"Error calculating financial metrics: {e}")
        return 0, 0, 0, 0


def load_company_models():
    """Attempt to load company suggestion models from models2 directory."""
    # We'll return the loaded objects plus a report dict with file/existence/errors
    report = {}
    base = 'models2'
    files = {
        'm_ready': os.path.join(base, 'pipeline_investment_ready.pkl'),
        'm_investor': os.path.join(base, 'pipeline_investor_type.pkl'),
        'm_funding': os.path.join(base, 'pipeline_funding_range.pkl'),
        'le_investor': os.path.join(base, 'label_encoder_investor.pkl'),
        'le_funding': os.path.join(base, 'label_encoder_funding.pkl'),
    }

    loaded = dict.fromkeys(files.keys(), None)

    for key, path in files.items():
        if os.path.exists(path):
            try:
                loaded[key] = joblib.load(path)
                report[key] = {'path': path, 'status': 'loaded', 'error': None}
            except Exception as e:
                tb = traceback.format_exc()
                loaded[key] = None
                report[key] = {'path': path, 'status': 'error', 'error': str(e), 'traceback': tb}
        else:
            report[key] = {'path': path, 'status': 'missing', 'error': None}

    return loaded['m_ready'], loaded['m_investor'], loaded['m_funding'], loaded['le_investor'], loaded['le_funding'], report


def get_dynamic_investor_description(investor_type, company_data):
    """Generate dynamic description for investor type based on company data"""
    revenue = company_data['annual_revenue_lakhs'][0]
    team_size = company_data['team_size'][0]
    sector = company_data['sector'][0]
    age = company_data['company_age_years'][0]
    
    descriptions = {
        "Angel Investor": f"Based on your {revenue:.1f}L revenue and {team_size}-person team, Angel Investors are ideal. They typically invest ₹25L-₹5Cr in early-stage companies like yours ({age} years old) and provide mentorship. Your {sector} sector is particularly attractive to angels who understand the industry nuances.",
        
        "Venture Capital": f"With your {revenue:.1f}L annual revenue and {team_size} employees, VCs could be interested if you're showing strong growth. They typically invest ₹5Cr-₹50Cr for scaling {sector} companies. Your {age}-year track record suggests you might be ready for VC funding if you have 3x+ year-over-year growth.",
        
        "Corporate Venture": f"Your {sector} focus aligns well with Corporate Venture arms. Given your {revenue:.1f}L revenue and {team_size} team, corporates in your space could offer strategic partnerships alongside ₹2Cr-₹20Cr investments. They value companies that can enhance their existing ecosystem.",
        
        "Private Equity": f"Your {revenue:.1f}L revenue suggests you might need more growth before PE becomes viable. PE firms typically invest ₹10Cr+ in profitable {sector} companies with ₹5Cr+ revenue. Consider focusing on profitability and scaling to ₹5Cr+ annual revenue first.",
        
        "Crowdfunding": f"Your {sector} business could thrive on crowdfunding platforms. With {team_size} people and {revenue:.1f}L revenue, you're in a good position to raise ₹10L-₹2Cr from many small investors. This works especially well if you have a strong consumer brand or community.",
        
        "Family Office": f"Family offices could be perfect for your {age}-year {sector} company. They offer patient capital for businesses like yours with {revenue:.1f}L revenue and {team_size} employees. They typically invest ₹1Cr-₹10Cr and are less pressured by traditional fund cycles."
    }
    return descriptions.get(investor_type, f"Based on your company profile with {revenue:.1f}L revenue and {team_size} employees, consider exploring various funding options.")


def get_dynamic_funding_description(funding_range, company_data):
    """Generate dynamic description for funding range based on company data"""
    revenue = company_data['annual_revenue_lakhs'][0]
    required = company_data['required_investment_lakhs'][0]
    burn_rate = company_data['monthly_burn_rate_lakhs'][0]
    team_size = company_data['team_size'][0]
    
    descriptions = {
        "Seed": f"You're seeking ₹{required:.1f}L which aligns with Seed funding. With your current ₹{revenue:.1f}L revenue and {burn_rate:.1f}L monthly burn, this funding should give you {required/burn_rate:.1f} months of runway. Use this to reach ₹50L+ annual revenue and expand your {team_size}-person team to 15-20 people.",
        
        "Early Stage": f"Your request for ₹{required:.1f}L fits Early Stage funding. Given your ₹{revenue:.1f}L current revenue, this investment should help you scale to ₹2-5Cr annually. With your {team_size}-person team, focus on product-market fit and customer acquisition efficiency.",
        
        "Growth Stage": f"At ₹{revenue:.1f}L revenue, you're approaching Growth Stage. The ₹{required:.1f}L you're seeking will help expand into new markets and scale your {team_size}-person team. Target achieving ₹10Cr+ revenue within 18-24 months.",
        
        "Late Stage": f"Your ₹{revenue:.1f}L revenue suggests you might be premature for Late Stage funding, which typically targets ₹50Cr+ revenue companies. Consider proving your business model further or repositioning as Growth Stage with a smaller ₹{required:.1f}L ask."
    }
    return descriptions.get(funding_range, f"Based on your request for ₹{required:.1f}L and current ₹{revenue:.1f}L revenue, carefully plan your use of funds to achieve key milestones.")


def generate_dynamic_insights(input_data, ready_pred, inv_pred, fund_pred):
    """Generate detailed insights based on company data and model predictions"""
    insights = []
    revenue = input_data['annual_revenue_lakhs'][0]
    margin = input_data['profit_margin_pct'][0]
    burn = input_data['monthly_burn_rate_lakhs'][0]
    team = input_data['team_size'][0]
    age = input_data['company_age_years'][0]
    sector = input_data['sector'][0]
    model = input_data['business_model'][0]
    growth = input_data['growth_rate_pct'][0]
    users = input_data['monthly_active_users'][0]
    market = input_data['market_size_cr'][0]
    
    # Investment readiness insights
    if ready_pred == 1:
        insights.append(f"✅ Your {age}-year {sector} company shows strong investment readiness with ₹{revenue:.1f}L revenue")
        if revenue > 50:
            insights.append(f"✅ Strong ₹{revenue:.1f}L revenue demonstrates market validation")
        if margin > 10:
            insights.append(f"✅ {margin:.1f}% profit margin indicates efficient operations")
        if growth > 20:
            insights.append(f"✅ {growth:.1f}% growth rate is highly attractive to investors")
    else:
        insights.append("⚠️ Focus on improving key metrics before seeking investment")
        if revenue < 20:
            insights.append(f"💡 Increase revenue from ₹{revenue:.1f}L to ₹50L+ to demonstrate market traction")
        if margin < 5:
            insights.append(f"💡 Improve {margin:.1f}% margin through cost optimization or pricing strategy")
        if burn > revenue/12:
            insights.append(f"💡 Reduce ₹{burn:.1f}L burn rate to extend runway")
    
    # Sector-specific insights
    sector_insights = {
        "AI/ML": [
            f"🤖 AI/ML companies with {users:,} users can command 8-12x revenue multiples",
            "💡 Highlight IP portfolio and technical team expertise"
        ],
        "SaaS": [
            f"☁️ SaaS metrics: Focus on ARR from ₹{revenue:.1f}L and churn rate",
            "💡 Emphasize MRR growth and customer lifetime value"
        ],
        "E-commerce": [
            f"🛒 With {users:,} MAU, focus on conversion rate and average order value",
            "💡 Highlight customer acquisition cost and retention metrics"
        ],
        "HealthTech": [
            f"🏥 HealthTech valued on clinical outcomes and regulatory approvals",
            "💡 Emphasize patient outcomes and healthcare partnerships"
        ],
        "FinTech": [
            f"💳 FinTech with {users:,} users valued on transaction volume and engagement",
            "💡 Focus on compliance and security certifications"
        ],
        "EdTech": [
            f"📚 EdTech companies valued on user engagement and learning outcomes",
            "💡 Highlight completion rates and educational impact"
        ]
    }
    if sector in sector_insights:
        insights.extend(sector_insights[sector])
    
    # Business model insights
    if model == "Subscription":
        insights.append(f"🔄 Subscription model: Your {revenue:.1f}L revenue should be framed as ARR")
        insights.append("💡 Target 3%+ monthly churn rate for healthy metrics")
    elif model == "Marketplace":
        insights.append(f"🏪 Marketplace: Focus on GMV from {users:,} users and take rate")
        insights.append("💡 Highlight liquidity metrics and network effects")
    elif model == "B2B":
        insights.append(f"🏢 B2B: Your {team}-person team should emphasize enterprise sales cycle")
        insights.append("💡 Focus on LTV:CAC ratio > 3:1")
    
    # Team insights
    if team < 5:
        insights.append(f"👥 Small {team}-person team: Emphasize founder expertise and adaptability")
    elif team > 50:
        insights.append(f"👥 Large {team}-person team: Highlight organizational structure and scalability")
    else:
        insights.append(f"👥 {team}-person team is optimal for current growth stage")
    
    # Financial health insights
    runway = (revenue * margin / 100 * 12) / burn if burn > 0 else 999
    if runway < 6:
        insights.append(f"⚠️ Current runway is {runway:.1f} months - urgent funding needed")
    elif runway > 24:
        insights.append(f"✅ Strong {runway:.1f} months runway provides negotiation leverage")
    
    # Market insights
    if market > 1000:
        insights.append(f"🌍 ₹{market:.0f}Cr market offers significant scaling opportunities")
    elif market < 100:
        insights.append(f"🎯 ₹{market:.0f}Cr niche market requires clear differentiation")
    
    return insights


def generate_actionable_recommendations(input_data, ready_pred, inv_label, fund_label):
    """Generate specific actionable recommendations"""
    recommendations = []
    revenue = input_data['annual_revenue_lakhs'][0]
    margin = input_data['profit_margin_pct'][0]
    burn = input_data['monthly_burn_rate_lakhs'][0]
    team = input_data['team_size'][0]
    age = input_data['company_age_years'][0]
    sector = input_data['sector'][0]
    required = input_data['required_investment_lakhs'][0]
    growth = input_data['growth_rate_pct'][0]
    
    # Investment readiness recommendations
    if ready_pred == 0:
        if revenue < 50:
            recommendations.append(f"Scale revenue to ₹50L+ before approaching {inv_label}s")
        if margin < 10:
            recommendations.append(f"Improve margins from {margin:.1f}% to 15%+ through pricing optimization")
        if burn > revenue/12:
            recommendations.append(f"Reduce burn from ₹{burn:.1f}L to ≤₹{revenue/24:.1f}L/month")
    
    # Investor-specific recommendations
    if inv_label == "Angel Investor":
        recommendations.append("Prepare 3-year financial projections with clear milestones")
        recommendations.append("Identify 3-5 angels with {sector} experience")
        recommendations.append("Create a compelling narrative around your {age}-year journey")
    elif inv_label == "Venture Capital":
        recommendations.append("Build detailed metrics dashboard showing growth trajectory")
        recommendations.append("Prepare for due diligence: clean cap table, IP documentation")
        recommendations.append("Identify reference customers for validation calls")
    elif inv_label == "Corporate Venture":
        recommendations.append("Map strategic synergies with potential corporate partners")
        recommendations.append("Prepare pilot program proposals for corporate collaboration")
        recommendations.append("Highlight how your solution enhances corporate value proposition")
    
    # Funding-specific recommendations
    if fund_label == "Seed":
        recommendations.append("Focus on product-market fit metrics: retention >40%, NPS >30")
        recommendations.append("Build advisory board with industry experts")
    elif fund_label == "Early Stage":
        recommendations.append("Develop scalable customer acquisition channels")
        recommendations.append("Implement robust analytics and reporting systems")
    elif fund_label == "Growth Stage":
        recommendations.append("Expand into 2-3 new geographic markets")
        recommendations.append("Build senior leadership team for scaling")
    
    # Sector-specific recommendations
    if sector == "AI/ML":
        recommendations.append("Secure IP patents and publish research papers")
        recommendations.append("Build technical advisory board with AI experts")
    elif sector == "SaaS":
        recommendations.append("Optimize pricing tiers based on usage analytics")
        recommendations.append("Implement customer success team to reduce churn")
    
    # Team recommendations
    if team < 10:
        recommendations.append("Hire key roles: product manager, sales lead, marketing head")
    elif team < 50:
        recommendations.append("Build middle management layer for scalability")
    
    # Financial recommendations
    if required > revenue * 2:
        recommendations.append(f"Consider reducing ask from ₹{required:.1f}L to ₹{revenue*1.5:.1f}L")
        recommendations.append("Break funding into milestones tied to KPIs")
    
    return recommendations


def run_company_flow():
    st.markdown('<h2 class="sub-header">🏢 Company Suggestion Model</h2>', unsafe_allow_html=True)
    st.info("Provide company details below to receive investment suggestions based on trained models.")

    m_ready, m_investor, m_funding, le_investor, le_funding, load_report = load_company_models()

    with st.form('company_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            company_age_years = st.number_input('Company Age (years)', min_value=0, max_value=100, value=3, help="How long has your company been operating?")
            annual_revenue_lakhs = st.number_input('Annual Revenue (lakhs)', min_value=0.0, value=20.0, help="Total revenue in the last 12 months (1 lakh = 100,000)")
            profit_margin_pct = st.number_input('Profit Margin (%)', value=5.0, help="Net profit as a percentage of revenue")
            monthly_burn_rate_lakhs = st.number_input('Monthly Burn Rate (lakhs)', min_value=0.0, value=1.0, help="Monthly cash outflow if expenses exceed revenue")
        with col2:
            market_size_cr = st.number_input('Market Size (cr)', min_value=0.0, value=100.0, help="Total addressable market size in crores (1 crore = 10 million)")
            team_size = st.number_input('Team Size', min_value=1, max_value=1000, value=10, help="Current number of employees")
            sector = st.selectbox('Sector', options=['AI/ML','E-commerce','EdTech','SaaS','HealthTech','FinTech','Entertainment','AgriTech'], help="Primary industry sector of your business")
            business_model = st.selectbox('Business Model', options=['Subscription','B2B','B2C','Marketplace','B2B2C'], help="How your company generates revenue")
        with col3:
            required_investment_lakhs = st.number_input('Required Investment (lakhs)', min_value=0.0, value=25.0, help="Amount of funding you're seeking")
            monthly_active_users = st.number_input('Monthly Active Users', min_value=0, value=10000, help="Number of active users per month")
            growth_rate_pct = st.number_input('Growth Rate (%)', value=5.0, help="Year-over-year revenue or user growth rate")

        submit = st.form_submit_button('Suggest for Company')

    if submit:
        input_df = pd.DataFrame([{
            'company_age_years': company_age_years,
            'annual_revenue_lakhs': annual_revenue_lakhs,
            'profit_margin_pct': profit_margin_pct,
            'monthly_burn_rate_lakhs': monthly_burn_rate_lakhs,
            'market_size_cr': market_size_cr,
            'team_size': team_size,
            'sector': sector,
            'business_model': business_model,
            'required_investment_lakhs': required_investment_lakhs,
            'monthly_active_users': monthly_active_users,
            'growth_rate_pct': growth_rate_pct
        }])

        # If none of the models loaded, show a helpful diagnostic.
        missing_all = all(load_report[k]['status'] == 'missing' for k in load_report)
        any_errors = any(load_report[k]['status'] == 'error' for k in load_report)

        if missing_all:
            st.error('No company models found in `models2/`. Please add the trained pipeline files there.')
            st.write('Expected files:')
            for k, info in load_report.items():
                st.write(f"- {info['path']}")
            return

        if any_errors:
            st.error('One or more model files were found but failed to load. See details below:')
            for k, info in load_report.items():
                if info['status'] == 'error':
                    st.markdown(f"**File**: `{info['path']}` — error: {info['error']}")
                    with st.expander('View traceback'):
                        st.code(info.get('traceback', 'No traceback available'))
            st.info('Common causes: missing dependency (e.g., xgboost), incompatible library versions, or corrupted model files.')
            st.warning('If the problem is a missing package, try installing it (for example: `pip install xgboost`) and re-run the app.')
            return

        with st.spinner('Running company suggestion models...'):
            time.sleep(0.8)
            try:
                # Initialize variables
                ready_pred = None
                inv_pred = None
                fund_pred = None
                
                # Get predictions from models
                if m_ready is not None:
                    ready_pred = m_ready.predict(input_df)[0]
                if m_investor is not None:
                    inv_pred = m_investor.predict(input_df)[0]
                    if le_investor is not None:
                        try:
                            inv_label = le_investor.inverse_transform([int(inv_pred)])[0]
                        except Exception:
                            inv_label = str(inv_pred)
                    else:
                        inv_label = str(inv_pred)
                if m_funding is not None:
                    fund_pred = m_funding.predict(input_df)[0]
                    if le_funding is not None:
                        try:
                            fund_label = le_funding.inverse_transform([int(fund_pred)])[0]
                        except Exception:
                            fund_label = str(fund_pred)
                    else:
                        fund_label = str(fund_pred)
                
                # Display results in a more organized way
                st.markdown('<h3 class="sub-header">📊 Investment Analysis Results</h3>', unsafe_allow_html=True)
                
                # Investment readiness
                if ready_pred is not None:
                    ready_status = "Ready for Investment" if ready_pred == 1 else "Not Ready for Investment"
                    ready_color = "positive" if ready_pred == 1 else "negative"
                    st.markdown(f"""
                    <div class="result-box">
                        <h3>Investment Readiness: <span class="{ready_color}">{ready_status}</span></h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create columns for results
                col1, col2 = st.columns(2)
                
                with col1:
                    if inv_label is not None:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Recommended Investor Type</h4>
                            <p>{inv_label}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add dynamic investor type description
                        with st.expander(f"About {inv_label} for your company"):
                            st.write(get_dynamic_investor_description(inv_label, input_df))
                
                with col2:
                    if fund_label is not None:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Suggested Funding Range</h4>
                            <p>{fund_label}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add dynamic funding range description
                        with st.expander(f"About {fund_label} Funding for your company"):
                            st.write(get_dynamic_funding_description(fund_label, input_df))
                
                # Generate and display insights
                insights = generate_dynamic_insights(input_df, ready_pred, inv_pred, fund_label)
                
                st.markdown('<h3 class="sub-header">💡 Company-Specific Insights</h3>', unsafe_allow_html=True)
                
                # Display insights in columns
                col1, col2 = st.columns(2)
                with col1:
                    for i, insight in enumerate(insights[:len(insights)//2]):
                        st.markdown(f"<p>{insight}</p>", unsafe_allow_html=True)
                with col2:
                    for i, insight in enumerate(insights[len(insights)//2:]):
                        st.markdown(f"<p>{insight}</p>", unsafe_allow_html=True)
                
                # Add actionable recommendations
                recommendations = generate_actionable_recommendations(input_df, ready_pred, inv_label, fund_label)
                
                st.markdown('<h3 class="sub-header">🎯 Actionable Recommendations</h3>', unsafe_allow_html=True)
                
                # Display recommendations
                for i, rec in enumerate(recommendations):
                    st.markdown(f"<p>📌 {rec}</p>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f'Error running company models: {e}')

# If user chose Company role, run company flow and stop further investor UI rendering
if role == "Company":
    run_company_flow()
    st.stop()

# --- Main Page Content for Investor ---
st.markdown('<h2 class="sub-header">📊 Investment Prediction Model - Project Parameters</h2>', unsafe_allow_html=True)

# Create columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    initial_cost = st.number_input(
        "Initial Cost ($)", 
        min_value=-1000000, 
        max_value=0, 
        value=-100000, 
        step=1000, 
        help="Initial investment cost (negative value)"
    )
    discount_rate = st.number_input(
        "Discount Rate (%)", 
        min_value=0.0, 
        max_value=50.0, 
        value=10.0, 
        step=0.1, 
        help="Annual discount rate for NPV calculation"
    )

with col2:
    duration_years = st.slider(
        "Project Duration (Years)", 
        min_value=1, 
        max_value=10, 
        value=5, 
        help="Expected duration of the project in years"
    )
    risk_rating = st.selectbox(
        "Risk Rating", 
        options=["Low", "Medium", "High"], 
        index=1
    )

with col3:
    project_type = st.selectbox(
        "Project Type", 
        options=["Retail", "Tech", "Healthcare", "Energy", "Infra"], 
        index=0
    )
    market_condition = st.selectbox(
        "Market Condition", 
        options=["Stable", "Unstable", "Volatile"], 
        index=0
    )

# --- Main Content Area --
# --- Main Analysis ---
if st.button("🔍 Analyze Investment", type="primary"):
    if regressor_model is None or classifier_model is None:
        st.error("Models could not be loaded. Please check the model files and try again.")
    else:
        # Show loading spinner
        with st.spinner("Analyzing investment opportunity..."):
            # Simulate processing time for better UX
            time.sleep(1.5)
            
            try:
                years = list(range(1, duration_years + 1))
                prediction_data = pd.DataFrame({
                    'Year': years,
                    'Risk_Rating': [risk_rating] * duration_years,
                    'Project_Type': [project_type] * duration_years,
                    'Market_Condition': [market_condition] * duration_years
                })
                prediction_data = prediction_data.astype(str)

                predicted_cash_flows = regressor_model.predict(prediction_data)
                predicted_cash_flows = np.maximum(predicted_cash_flows, 0)

                npv, irr, pi, payback_period = calculate_financial_metrics(initial_cost, discount_rate, predicted_cash_flows)
                total_inflows = np.sum(predicted_cash_flows)
                avg_cash_flow = np.mean(predicted_cash_flows)
                cf_volatility = np.std(predicted_cash_flows)

                classifier_data = pd.DataFrame({
                    'Initial_Cost': [initial_cost],
                    'Discount_Rate_%': [discount_rate],
                    'Risk_Rating': [risk_rating],
                    'Project_Type': [project_type],
                    'Market_Condition': [market_condition],
                    'Duration_Years': [duration_years],
                    'Total_Cash_Inflows': [total_inflows],
                    'Avg_Cash_Flow': [avg_cash_flow],
                    'CF_Volatility': [cf_volatility]
                }).astype(str)

                decision = classifier_model.predict(classifier_data)[0]
                decision_proba = classifier_model.predict_proba(classifier_data)[0]
                confidence = max(decision_proba) * 100

                st.markdown('<h2 class="sub-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
                decision_color = "positive" if decision == "accept" else "negative"
                st.markdown(f"""
                <div class="result-box">
                    <h3>Investment Decision: <span class="{decision_color}">{decision.upper()}</span></h3>
                    <p>Confidence: {confidence:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)

                # Metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    npv_color = "positive" if npv > 0 else "negative"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Net Present Value</h4>
                        <p class="{npv_color}">${npv:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    irr_color = "positive" if irr > discount_rate else "negative"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Internal Rate of Return</h4>
                        <p class="{irr_color}">{irr:.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    pi_color = "positive" if pi > 1 else "negative"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Profitability Index</h4>
                        <p class="{pi_color}">{pi:.3f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    payback_color = "positive" if payback_period <= duration_years * 0.5 else "warning" if payback_period <= duration_years else "negative"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Payback Period</h4>
                        <p class="{payback_color}">{payback_period:.1f} years</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Cash Flow Visualization
                st.markdown('<h2 class="sub-header">📈 Predicted Cash Flows</h2>', unsafe_allow_html=True)
                cf_df = pd.DataFrame({
                    'Year': years,
                    'Predicted Cash Flow': predicted_cash_flows,
                    'Cumulative Cash Flow': np.cumsum(predicted_cash_flows)
                })
                st.line_chart(cf_df.set_index('Year'))

                # Cash Flow Details in Expander
                with st.expander("View Cash Flow Details"):
                    cf_table = pd.DataFrame({
                        'Year': years,
                        'Cash Flow': [f"${cf:,.2f}" for cf in predicted_cash_flows],
                        'Cumulative': [f"${cf:,.2f}" for cf in np.cumsum(predicted_cash_flows)]
                    })
                    st.table(cf_table)

                # Investment Insights
                st.markdown('<h2 class="sub-header">💡 Investment Insights</h2>', unsafe_allow_html=True)
                insights = []
                if npv > 0:
                    insights.append("✅ Positive NPV indicates the project is expected to generate value")
                else:
                    insights.append("❌ Negative NPV suggests the project may not be profitable")
                if irr > discount_rate:
                    insights.append("✅ IRR exceeds the discount rate, indicating good return potential")
                else:
                    insights.append("❌ IRR is below the discount rate, consider alternative investments")
                if pi > 1:
                    insights.append("✅ PI > 1 means the project creates value for each dollar invested")
                else:
                    insights.append("❌ PI < 1 indicates the project destroys value")
                if payback_period <= duration_years * 0.5:
                    insights.append("✅ Quick payback period reduces investment risk")
                elif payback_period <= duration_years:
                    insights.append("⚠️ Moderate payback period")
                else:
                    insights.append("❌ Payback period exceeds project duration")
                if risk_rating == "High":
                    insights.append("⚠️ High risk project requires careful consideration")
                elif risk_rating == "Low":
                    insights.append("✅ Low risk project with stable returns expected")
                
                # Display insights in columns
                col1, col2 = st.columns(2)
                with col1:
                    for i, insight in enumerate(insights[:len(insights)//2]):
                        st.markdown(f"<p>{insight}</p>", unsafe_allow_html=True)
                with col2:
                    for i, insight in enumerate(insights[len(insights)//2:]):
                        st.markdown(f"<p>{insight}</p>", unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
                st.error("Please check your input values and try again.")

# --- Enhanced Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 1rem 0;'>
    <p>Investment Decision Predictor | Powered by Machine Learning</p>
    <p style='font-size: 0.9rem; margin-bottom: 1rem;'>This tool provides predictions based on historical data and should not be the sole basis for investment decisions.</p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# Page config
st.set_page_config(
    page_title="AI Lead Finder - TOI News Platform",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'leads_generated' not in st.session_state:
    st.session_state.leads_generated = False

# HEADER
st.markdown('<div class="main-header">🎯 AI Lead Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">For TOI News Digital Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# SIDEBAR
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("", [
    "🏠 Home",
    "📈 Analytics Analyzer", 
    "🎯 Lead Generator",
    "🔍 Contact Helper",
    "📧 Email Generator"
])

st.sidebar.markdown("---")
st.sidebar.info("💡 Start with Analytics Analyzer!")

# Classes
class AnalyticsAnalyzer:
    def __init__(self, df):
        self.df = df
    
    def extract_category(self, title):
        categories = {
            'Technology': ['tech', 'software', 'ai', 'app', 'digital'],
            'Real Estate': ['property', 'real estate', 'housing'],
            'Finance': ['bank', 'finance', 'loan', 'investment'],
            'Education': ['education', 'school', 'college'],
            'Healthcare': ['health', 'hospital', 'medical'],
            'Automotive': ['car', 'auto', 'vehicle'],
            'E-commerce': ['shopping', 'online', 'ecommerce'],
            'Travel': ['travel', 'hotel', 'tourism'],
            'Food': ['restaurant', 'food', 'cafe'],
            'Entertainment': ['movie', 'entertainment', 'music']
        }
        title_lower = str(title).lower()
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        return 'General'
    
    def analyze(self):
        title_col = None
        views_col = None
        for col in self.df.columns:
            if any(k in col.lower() for k in ['page', 'title', 'url']):
                title_col = col
            if any(k in col.lower() for k in ['view', 'pageview']):
                views_col = col
        if title_col and views_col:
            self.df[views_col] = pd.to_numeric(self.df[views_col], errors='coerce')
            self.df['Category'] = self.df[title_col].apply(self.extract_category)
            return True
        return False

class LeadGenerator:
    def __init__(self):
        self.business_mapping = {
            'Technology': ['Software Companies', 'IT Services', 'Tech Startups'],
            'Real Estate': ['Real Estate Developers', 'Property Consultants'],
            'Finance': ['Banks', 'Insurance Companies', 'Fintech Startups'],
            'Education': ['Coaching Centers', 'EdTech Companies'],
            'Healthcare': ['Hospitals', 'Pharmaceutical Companies'],
            'Automotive': ['Car Dealerships', 'Auto Parts'],
            'E-commerce': ['Online Retailers', 'D2C Brands'],
            'Travel': ['Travel Agencies', 'Hotels', 'OTAs'],
            'Food': ['Cloud Kitchens', 'Restaurant Chains'],
            'Entertainment': ['Streaming Services', 'Production Houses']
        }
    
    def generate_leads(self, categories, cities, num=10):
        leads = []
        for category in categories:
            if category in self.business_mapping:
                for business in self.business_mapping[category]:
                    for city in cities[:3]:
                        leads.append({
                            'Business_Type': business,
                            'Category': category,
                            'Target_Location': city,
                            'Search_Query': f"{business} in {city}",
                            'Why_Target': f"Your {category} content attracts {city} audience",
                            'LinkedIn': f"https://www.linkedin.com/search/results/companies/?keywords={business.replace(' ', '%20')}",
                            'Google': f"https://www.google.com/search?q={business.replace(' ', '+')}+in+{city}+contact"
                        })
        return pd.DataFrame(leads[:num])

# PAGE: HOME
if page == "🏠 Home":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h2>📊</h2><h3>Analyze</h3><p>Upload Analytics</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h2>🎯</h2><h3>Generate</h3><p>Find Leads</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h2>📧</h2><h3>Contact</h3><p>Reach Out</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🚀 How It Works")
    st.write("1. Upload your Google Analytics CSV")
    st.write("2. AI analyzes your content categories")
    st.write("3. Generates qualified business leads")
    st.write("4. Provides search URLs to find contacts")
    st.write("5. Creates personalized email templates")

# PAGE: ANALYTICS
elif page == "📈 Analytics Analyzer":
    st.header("📈 Analytics Analyzer")
    uploaded_file = st.file_uploader("Upload Google Analytics CSV", type=['csv'])
    
    if uploaded_file:
        try:
            df = None
            for skip in [0, 6, 7, 8]:
                try:
                    df = pd.read_csv(uploaded_file, skiprows=skip, on_bad_lines='skip')
                    if len(df) > 0 and len(df.columns) > 3:
                        break
                except:
                    continue
            
            if df is not None and len(df) > 0:
                st.success(f"✅ Loaded {len(df)} rows!")
                analyzer = AnalyticsAnalyzer(df)
                
                if analyzer.analyze():
                    st.session_state.analyzer_df = analyzer.df
                    category_counts = analyzer.df['Category'].value_counts()
                    
                    fig = px.pie(values=category_counts.values, names=category_counts.index, title="Categories")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.session_state.top_categories = category_counts.index.tolist()
                    st.session_state.default_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune']
                    st.success("✅ Ready! Go to Lead Generator")
        except Exception as e:
            st.error(f"Error: {e}")

# PAGE: LEAD GENERATOR
elif page == "🎯 Lead Generator":
    st.header("🎯 Lead Generator")
    
    col1, col2 = st.columns(2)
    with col1:
        if 'top_categories' in st.session_state:
            categories = st.multiselect("Categories", st.session_state.top_categories, st.session_state.top_categories[:3])
        else:
            categories = st.multiselect("Categories", ['Technology', 'Finance', 'Real Estate'], ['Technology'])
    
    with col2:
        if 'default_cities' in st.session_state:
            cities = st.multiselect("Cities", st.session_state.default_cities, st.session_state.default_cities[:3])
        else:
            cities = st.multiselect("Cities", ['Mumbai', 'Delhi', 'Bangalore'], ['Mumbai'])
    
    num_leads = st.slider("Number of leads", 10, 100, 50)
    
    if st.button("🚀 Generate Leads", type="primary"):
        if categories and cities:
            generator = LeadGenerator()
            leads_df = generator.generate_leads(categories, cities, num_leads)
            st.session_state.leads_df = leads_df
            
            st.success(f"✅ Generated {len(leads_df)} leads!")
            st.dataframe(leads_df[['Business_Type', 'Category', 'Target_Location', 'Why_Target']])
            
            csv = leads_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, f"leads_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.error("Select categories and cities!")

# PAGE: CONTACT HELPER
elif page == "🔍 Contact Helper":
    st.header("🔍 Contact Helper")
    
    if 'leads_df' in st.session_state:
        leads_df = st.session_state.leads_df
        st.success(f"You have {len(leads_df)} leads!")
        
        idx = st.selectbox("Select lead", range(len(leads_df)), format_func=lambda x: f"{leads_df.iloc[x]['Business_Type']} in {leads_df.iloc[x]['Target_Location']}")
        lead = leads_df.iloc[idx]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Google Search")
            st.link_button("Search Google", lead['Google'], use_container_width=True)
        with col2:
            st.markdown("### LinkedIn Search")
            st.link_button("Search LinkedIn", lead['LinkedIn'], use_container_width=True)
        
        st.markdown("---")
        st.subheader("Email Pattern Generator")
        company = st.text_input("Company Name", "Example Corp")
        domain = st.text_input("Website", "example.com")
        
        if st.button("Generate Patterns"):
            patterns = [f"info@{domain}", f"contact@{domain}", f"marketing@{domain}", f"sales@{domain}"]
            for p in patterns:
                st.code(p)
    else:
        st.warning("Generate leads first!")

# PAGE: EMAIL GENERATOR
elif page == "📧 Email Generator":
    st.header("📧 Email Generator")
    
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company Name", "Tech Corp")
        category = st.selectbox("Category", ['Technology', 'Finance', 'Real Estate'])
        location = st.text_input("Location", "Mumbai")
    with col2:
        your_name = st.text_input("Your Name", "Rahul Sharma")
        your_title = st.text_input("Your Title", "Business Manager")
        platform = st.text_input("Platform", "TOI News Digital")
    
    traffic = st.text_input("Traffic Stat", "3 million daily readers")
    
    if st.button("✨ Generate Email", type="primary"):
        email = f"""Subject: Partnership Opportunity - {platform} & {company}

Dear {company} Team,

I'm {your_name}, {your_title} at {platform}, reaching {traffic}.

We've noticed strong engagement from {category} readers in {location}, and believe {company} could benefit from this audience.

Would you be open to a 15-minute call to explore partnership opportunities?

Best regards,
{your_name}
{your_title}
{platform}
"""
        st.text_area("Generated Email", email, height=300)
        st.download_button("⬇️ Download", email, f"email_{company}.txt", "text/plain")

st.markdown("---")
st.markdown("<div style='text-align: center;'><p>🎯 AI Lead Finder v1.0</p></div>", unsafe_allow_html=True)

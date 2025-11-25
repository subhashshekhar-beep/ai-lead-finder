
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re
import time
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except:
    SCRAPING_AVAILABLE = False

st.set_page_config(page_title="AI Lead Finder", page_icon="🎯", layout="wide")

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

if 'leads_generated' not in st.session_state:
    st.session_state.leads_generated = False
if 'enriched_leads' not in st.session_state:
    st.session_state.enriched_leads = None

st.markdown('<div class="main-header">🎯 AI Lead Finder PRO</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 1.2rem; margin-bottom: 30px;">Automated Contact Discovery</div>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.title("📊 Dashboard")
page = st.sidebar.radio("Navigation", [
    "🏠 Home",
    "📈 Analytics Analyzer", 
    "🎯 Lead Generator",
    "🤖 Auto Contact Finder",
    "📧 Email Generator"
])

st.sidebar.markdown("---")
if 'leads_df' in st.session_state:
    st.sidebar.metric("Leads Generated", len(st.session_state.leads_df))
if 'enriched_leads' in st.session_state and st.session_state.enriched_leads is not None:
    st.sidebar.metric("Contacts Found", len(st.session_state.enriched_leads))

class ContactScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_google(self, query):
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for g in soup.find_all('div', class_='g')[:3]:
                try:
                    title_elem = g.find('h3')
                    link_elem = g.find('a')
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        url = link_elem.get('href', '')
                        if url.startswith('http') and 'google.com' not in url:
                            results.append({'name': title, 'website': url})
                except:
                    continue
            return results
        except:
            return []
    
    def extract_emails(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=8)
            text = response.text
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            valid_emails = [e for e in emails if not any(x in e.lower() for x in 
                ['example.com', 'sentry', 'schema.org', 'wix.com', 'google', 'facebook'])]
            return list(set(valid_emails))[:3]
        except:
            return []
    
    def extract_phones(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=8)
            text = response.text
            patterns = [r'\+91[\s-]?\d{10}', r'\b[6-9]\d{9}\b']
            phones = []
            for pattern in patterns:
                phones.extend(re.findall(pattern, text))
            return list(set(phones))[:2]
        except:
            return []
    
    def generate_email_patterns(self, domain):
        domain = domain.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]
        return [f"info@{domain}", f"contact@{domain}", f"marketing@{domain}", f"sales@{domain}"]
    
    def enrich_lead(self, search_query, category, location):
        result = {
            'Search_Query': search_query,
            'Category': category,
            'Location': location,
            'Company_Name': '',
            'Website': '',
            'Email_Found': [],
            'Phone_Found': [],
            'Email_Patterns': [],
            'Status': 'Not Found'
        }
        
        companies = self.search_google(search_query)
        if not companies:
            return result
        
        company = companies[0]
        result['Company_Name'] = company['name']
        result['Website'] = company['website']
        
        emails = self.extract_emails(company['website'])
        phones = self.extract_phones(company['website'])
        
        result['Email_Found'] = emails
        result['Phone_Found'] = phones
        
        if not emails:
            result['Email_Patterns'] = self.generate_email_patterns(company['website'])
        
        if emails or phones:
            result['Status'] = 'Verified'
        elif result['Email_Patterns']:
            result['Status'] = 'Patterns Generated'
        else:
            result['Status'] = 'Manual Review'
        
        return result

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
            'Travel': ['Travel Agencies', 'Hotels'],
            'Food': ['Restaurant Chains', 'Food Tech'],
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
                            'Why_Target': f"Your {category} content attracts {city} audience"
                        })
                        if len(leads) >= num:
                            break
                if len(leads) >= num:
                    break
        return pd.DataFrame(leads[:num])

if page == "🏠 Home":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h2>📊</h2><h3>Analyze</h3></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h2>🎯</h2><h3>Generate</h3></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h2>🤖</h2><h3>Auto-Find</h3></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🚀 How It Works")
    st.write("1. Upload Google Analytics (optional)")
    st.write("2. Generate 10-50 business leads")
    st.write("3. Auto-find emails & phones")
    st.write("4. Download enriched contacts")
    st.write("5. Use AI email templates to reach out")

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
                    
                    fig = px.pie(values=category_counts.values, names=category_counts.index, 
                               title="Content Distribution", hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.session_state.top_categories = category_counts.index.tolist()
                    st.session_state.default_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune']
                    st.success("✅ Ready! Go to Lead Generator")
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "🎯 Lead Generator":
    st.header("🎯 Lead Generator")
    
    col1, col2 = st.columns(2)
    with col1:
        if 'top_categories' in st.session_state:
            categories = st.multiselect("Categories", st.session_state.top_categories, 
                                       st.session_state.top_categories[:3])
        else:
            categories = st.multiselect("Categories", 
                                       ['Technology', 'Finance', 'Real Estate', 'Education'],
                                       ['Technology', 'Finance'])
    
    with col2:
        if 'default_cities' in st.session_state:
            cities = st.multiselect("Cities", st.session_state.default_cities, 
                                   st.session_state.default_cities[:3])
        else:
            cities = st.multiselect("Cities", 
                                   ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad'],
                                   ['Mumbai', 'Delhi'])
    
    num_leads = st.slider("Number of leads", 5, 50, 20)
    
    if st.button("🚀 Generate Leads", type="primary"):
        if categories and cities:
            generator = LeadGenerator()
            leads_df = generator.generate_leads(categories, cities, num_leads)
            st.session_state.leads_df = leads_df
            
            st.success(f"✅ Generated {len(leads_df)} leads!")
            st.dataframe(leads_df[['Business_Type', 'Category', 'Target_Location']])
            
            csv = leads_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download", csv, 
                             f"leads_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            
            st.info("👉 Go to 'Auto Contact Finder' next!")
        else:
            st.error("Select categories and cities!")

elif page == "🤖 Auto Contact Finder":
    st.header("🤖 Automatic Contact Finder")
    
    if 'leads_df' not in st.session_state:
        st.warning("⚠️ Generate leads first!")
        st.info("Go to 'Lead Generator' to create leads.")
    else:
        leads_df = st.session_state.leads_df
        st.success(f"✅ You have {len(leads_df)} leads!")
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_to_process = min(50, len(leads_df))
            default_num = min(10, len(leads_df))
            num_to_process = st.slider("How many to process?", 1, max_to_process, default_num)
            st.info(f"⏱️ Time: ~{num_to_process * 6} seconds")
        
        with col2:
            st.markdown("**Process:**")
            st.write("1. Search Google")
            st.write("2. Visit websites")
            st.write("3. Extract emails/phones")
            st.write("4. Generate patterns")
        
        st.markdown("---")
        
        if st.button("🚀 Start Finding Contacts", type="primary", use_container_width=True):
            scraper = ContactScraper()
            enriched_results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, row in leads_df.head(num_to_process).iterrows():
                status_text.text(f"Processing {idx+1}/{num_to_process}: {row['Search_Query']}")
                
                result = scraper.enrich_lead(row['Search_Query'], row['Category'], row['Target_Location'])
                enriched_results.append(result)
                
                progress_bar.progress((idx + 1) / num_to_process)
                time.sleep(1)
            
            status_text.text("✅ Complete!")
            
            enriched_df = pd.DataFrame(enriched_results)
            st.session_state.enriched_leads = enriched_df
            
            st.markdown("---")
            st.markdown("### 📊 Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Processed", len(enriched_df))
            with col2:
                verified = len(enriched_df[enriched_df['Status'] == 'Verified'])
                st.metric("Emails Found", verified)
            with col3:
                rate = int((verified / len(enriched_df)) * 100) if len(enriched_df) > 0 else 0
                st.metric("Success Rate", f"{rate}%")
            
            st.markdown("---")
            
            for idx, row in enriched_df.iterrows():
                with st.expander(f"{row['Company_Name']} - {row['Status']}"):
                    st.write(f"**Website:** {row['Website']}")
                    st.write(f"**Category:** {row['Category']}")
                    if row['Email_Found']:
                        st.write(f"**Emails:** {', '.join(row['Email_Found'])}")
                    if row['Phone_Found']:
                        st.write(f"**Phones:** {', '.join(row['Phone_Found'])}")
                    if row['Email_Patterns']:
                        st.write(f"**Try these:** {', '.join(row['Email_Patterns'])}")
            
            csv = enriched_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download All Results", csv,
                             f"contacts_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

elif page == "📧 Email Generator":
    st.header("📧 Email Generator")
    
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company", "Tech Corp")
        category = st.selectbox("Category", ['Technology', 'Finance', 'Real Estate'])
        location = st.text_input("Location", "Mumbai")
    with col2:
        your_name = st.text_input("Your Name", "Rahul")
        your_title = st.text_input("Title", "Business Manager")
        platform = st.text_input("Platform", "TOI News")
    
    if st.button("✨ Generate", type="primary"):
        email = f"""Subject: Partnership - {platform} & {company}

Dear {company} Team,

I'm {your_name}, {your_title} at {platform}.

We see strong engagement from {category} readers in {location}. Would love to discuss advertising opportunities.

15-minute call this week?

Best,
{your_name}
{platform}
"""
        st.text_area("Email:", email, height=300)
        st.download_button("⬇️ Download", email, f"email_{company}.txt", "text/plain")

st.markdown("---")
st.markdown("<div style='text-align: center;'><p>🎯 AI Lead Finder PRO v2.0</p></div>", unsafe_allow_html=True)

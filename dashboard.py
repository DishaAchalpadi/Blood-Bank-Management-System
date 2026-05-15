import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Blood Bank Management Dashboard",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .header-style {
        color: #e74c3c;
        font-weight: bold;
        border-bottom: 3px solid #e74c3c;
        padding-bottom: 10px;
    }
    .tab-style {
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette('husl')

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_blood_donor_dataset.csv')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['year'] = df['created_at'].dt.year
    df['month'] = df['created_at'].dt.month
    df['quarter'] = df['created_at'].dt.quarter
    return df

df = load_data()

# Title and Description
col_title1, col_title2 = st.columns([3, 1])
with col_title1:
    st.title("🩸 Blood Bank Management System")
    st.markdown("**Interactive Dashboard for Blood Donor Database**")
with col_title2:
    st.metric("Data Points", len(df))

st.markdown("---")

# Sidebar - Advanced Filters
st.sidebar.header("⚙️ Advanced Filters")

# Search donor by ID or name
search_donor = st.sidebar.text_input("🔍 Search Donor (ID/Name):", "")

# Blood group filter
blood_groups = st.sidebar.multiselect(
    "🩸 Select Blood Groups",
    options=sorted(df['blood_group'].unique()),
    default=sorted(df['blood_group'].unique()),
    help="Filter by blood group"
)

# City filter
cities = st.sidebar.multiselect(
    "📍 Select Cities",
    options=sorted(df['city'].unique()),
    default=sorted(df['city'].unique()),
    help="Filter by location"
)

# Availability filter
availabilities = st.sidebar.multiselect(
    "✅ Select Availability",
    options=df['availability'].unique(),
    default=df['availability'].unique(),
    help="Filter by donor availability"
)

# Donation frequency filter
min_donations, max_donations = st.sidebar.slider(
    "📊 Donation Count Range",
    min_value=int(df['number_of_donation'].min()),
    max_value=int(df['number_of_donation'].max()),
    value=(int(df['number_of_donation'].min()), int(df['number_of_donation'].max())),
    help="Filter donors by number of donations"
)

# Pints donated filter
min_pints, max_pints = st.sidebar.slider(
    "🩹 Pints Donated Range",
    min_value=int(df['pints_donated'].min()),
    max_value=int(df['pints_donated'].max()),
    value=(int(df['pints_donated'].min()), int(df['pints_donated'].max())),
    help="Filter by pints donated"
)

# Filter data
filtered_df = df[
    (df['blood_group'].isin(blood_groups)) &
    (df['city'].isin(cities)) &
    (df['availability'].isin(availabilities)) &
    (df['number_of_donation'] >= min_donations) &
    (df['number_of_donation'] <= max_donations) &
    (df['pints_donated'] >= min_pints) &
    (df['pints_donated'] <= max_pints)
]

# Apply search filter
if search_donor.strip():
    mask = (filtered_df['donor_id'].str.contains(search_donor, case=False, na=False)) | \
           (filtered_df['name'].str.contains(search_donor, case=False, na=False))
    filtered_df = filtered_df[mask]

# Check if filtered_df is empty
if len(filtered_df) == 0:
    st.warning("⚠️ No donors found matching your filters. Please adjust your search criteria.", icon="⚠️")
    # Show original data count
    st.info(f"Total donors in database: {len(df)}", icon="ℹ️")
    st.stop()


# Key metrics with better styling
active_filters = []
if search_donor.strip():
    active_filters.append(f"🔍 Search: '{search_donor}'")
if len(blood_groups) < len(df['blood_group'].unique()):
    active_filters.append(f"🩸 Blood Groups: {len(blood_groups)}")
if len(cities) < len(df['city'].unique()):
    active_filters.append(f"📍 Cities: {len(cities)}")
if len(availabilities) < len(df['availability'].unique()):
    active_filters.append(f"✅ Availability: {len(availabilities)}")

st.markdown("<h2 style='color: #e74c3c; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;'>📈 Key Metrics</h2>", unsafe_allow_html=True)

if active_filters:
    st.info("Active Filters: " + " | ".join(active_filters), icon="📋")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    st.metric(
        "👥 Total Donors",
        len(filtered_df),
        delta=f"{len(filtered_df)} selected",
        delta_color="off"
    )

with metric_col2:
    avg_donations = filtered_df['number_of_donation'].mean()
    st.metric("💉 Avg Donations", f"{avg_donations:.1f}", help="Average donations per donor")

with metric_col3:
    total_pints = filtered_df['pints_donated'].sum()
    st.metric("🩹 Total Pints", f"{total_pints:,}", help="Total pints donated")

with metric_col4:
    avail_rate = (filtered_df['availability'] == 'Yes').mean() * 100
    st.metric("✅ Availability %", f"{avail_rate:.1f}%", help="% of available donors")

with metric_col5:
    avg_months = filtered_df['months_since_first_donation'].mean()
    st.metric("📅 Avg Tenure", f"{avg_months:.0f} months", help="Average months since first donation")

st.markdown("---")

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "👥 Donor Analysis",
    "💉 Donation Trends",
    "🩸 Blood Inventory",
    "📍 Location Insights"
])

# TAB 1: OVERVIEW
with tab1:
    st.markdown("<h3 class='header-style'>Dashboard Overview</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🩸 Blood Group Distribution")
        blood_group_counts = filtered_df['blood_group'].value_counts()
        fig_bg = px.pie(
            values=blood_group_counts.values,
            names=blood_group_counts.index,
            title="Blood Group Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.3
        )
        fig_bg.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_bg, use_container_width=True)
    
    with col2:
        st.subheader("✅ Availability Status")
        avail_counts = filtered_df['availability'].value_counts()
        colors_avail = ['#2ecc71' if x == 'Yes' else '#e74c3c' for x in avail_counts.index]
        fig_avail = px.bar(
            x=avail_counts.index,
            y=avail_counts.values,
            title="Donor Availability",
            labels={'x': 'Availability', 'y': 'Count'},
            color=avail_counts.index,
            color_discrete_map={'Yes': '#2ecc71', 'No': '#e74c3c'}
        )
        fig_avail.update_layout(showlegend=False)
        st.plotly_chart(fig_avail, use_container_width=True)

# TAB 2: DONOR ANALYSIS
with tab2:
    st.markdown("<h3 class='header-style'>Donor Analysis</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Donor Distribution by City")
        city_counts = filtered_df['city'].value_counts().head(10)
        fig_city = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            title="Top 10 Cities by Donor Count",
            labels={'x': 'Number of Donors', 'y': 'City'},
            color=city_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_city, use_container_width=True)
    
    with col2:
        st.subheader("👥 Donor Demographics")
        # Age group analysis (inferred from months_since_first_donation)
        fig_age = px.histogram(
            filtered_df,
            x='months_since_first_donation',
            nbins=20,
            title="Distribution of Donor Tenure",
            labels={'months_since_first_donation': 'Months Since First Donation', 'count': 'Number of Donors'},
            color_discrete_sequence=['#3498db']
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    # Blood group and availability cross-tabulation
    st.subheader("🎯 Blood Group × Availability Matrix")
    cross_tab = pd.crosstab(filtered_df['blood_group'], filtered_df['availability'])
    fig_cross = px.imshow(
        cross_tab,
        text_auto=True,
        aspect="auto",
        title="Cross-tabulation: Blood Group vs Availability",
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_cross, use_container_width=True)

# TAB 3: DONATION TRENDS
with tab3:
    st.markdown("<h3 class='header-style'>Donation Trends & Analysis</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Donations Over Time")
        donations_per_year = filtered_df.groupby('year')['number_of_donation'].sum()
        fig_time = px.line(
            donations_per_year,
            title='Total Donations by Year',
            labels={'value': 'Total Donations', 'year': 'Year'},
            markers=True
        )
        fig_time.update_traces(line=dict(color='#e74c3c', width=3))
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        st.subheader("💉 Total Pints by Blood Group")
        total_pints_bg = filtered_df.groupby('blood_group')['pints_donated'].sum().sort_values(ascending=True)
        fig_pints = px.bar(
            x=total_pints_bg.values,
            y=total_pints_bg.index,
            orientation='h',
            title='Total Pints Donated by Blood Group',
            labels={'x': 'Total Pints', 'y': 'Blood Group'},
            color=total_pints_bg.values,
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_pints, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Months Since First Donation vs Donation Count")
        fig_scatter = px.scatter(
            filtered_df,
            x='months_since_first_donation',
            y='number_of_donation',
            color='blood_group',
            size='pints_donated',
            hover_data=['donor_id', 'city'],
            title="Donor Tenure vs Donation Frequency",
            labels={
                'months_since_first_donation': 'Months Since First Donation',
                'number_of_donation': 'Number of Donations'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        st.subheader("📊 Donation Statistics by Blood Group")
        donation_stats = filtered_df.groupby('blood_group').agg({
            'number_of_donation': ['mean', 'max', 'min'],
            'pints_donated': ['sum', 'mean']
        }).round(2)
        st.dataframe(donation_stats, use_container_width=True)

# TAB 4: BLOOD INVENTORY
with tab4:
    st.markdown("<h3 class='header-style'>Blood Inventory Analysis</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💾 Total Blood Units",
            f"{filtered_df['pints_donated'].sum():,}",
            help="Total pints available in inventory"
        )
    
    with col2:
        avg_inventory = filtered_df.groupby('blood_group')['pints_donated'].sum().mean()
        st.metric("📦 Avg per Blood Group", f"{avg_inventory:.0f}", help="Average pints per blood group")
    
    with col3:
        critical_stock = len(filtered_df[filtered_df['pints_donated'] < filtered_df['pints_donated'].quantile(0.25)])
        st.metric("⚠️ Low Stock Donors", critical_stock, help="Donors with below 25% pints")
    
    st.subheader("🩸 Blood Inventory by Group")
    inventory_data = filtered_df.groupby('blood_group').agg({
        'pints_donated': 'sum',
        'donor_id': 'count'
    }).rename(columns={'donor_id': 'Donor_Count', 'pints_donated': 'Total_Pints'}).sort_values('Total_Pints', ascending=False)
    
    fig_inventory = go.Figure(data=[
        go.Bar(
            x=inventory_data.index,
            y=inventory_data['Total_Pints'],
            name='Total Pints',
            marker_color='#e74c3c',
            text=inventory_data['Total_Pints'],
            textposition='outside'
        ),
        go.Scatter(
            x=inventory_data.index,
            y=inventory_data['Donor_Count'],
            name='Donor Count',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#3498db', width=3),
            marker=dict(size=10)
        )
    ])
    
    fig_inventory.update_layout(
        title='Blood Inventory & Donor Count by Blood Group',
        xaxis_title='Blood Group',
        yaxis_title='Total Pints',
        yaxis2=dict(title='Donor Count', overlaying='y', side='right'),
        hovermode='x unified'
    )
    st.plotly_chart(fig_inventory, use_container_width=True)

# TAB 5: LOCATION INSIGHTS
with tab5:
    st.markdown("<h3 class='header-style'>Geographic Insights</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 City-wise Performance")
        city_performance = filtered_df.groupby('city').agg({
            'donor_id': 'count',
            'pints_donated': 'sum',
            'number_of_donation': 'mean'
        }).rename(columns={
            'donor_id': 'Total_Donors',
            'pints_donated': 'Total_Pints',
            'number_of_donation': 'Avg_Donations'
        }).sort_values('Total_Donors', ascending=False)
        
        fig_city_perf = px.scatter(
            city_performance.reset_index(),
            x='Total_Donors',
            y='Total_Pints',
            size='Avg_Donations',
            hover_data=['city'],
            title='City Performance Matrix',
            labels={'Total_Donors': 'Total Donors', 'Total_Pints': 'Total Pints'},
            color_discrete_sequence=['#2ecc71']
        )
        st.plotly_chart(fig_city_perf, use_container_width=True)
    
    with col2:
        st.subheader("📊 City Rankings")
        st.dataframe(
            city_performance.reset_index().rename(columns={'city': 'City'}).style.format({
                'Total_Donors': '{:.0f}',
                'Total_Pints': '{:.0f}',
                'Avg_Donations': '{:.1f}'
            }),
            use_container_width=True
        )

st.markdown("---")

# DETAILED DATA TABLE
st.markdown("<h3 class='header-style'>📋 Detailed Donor Records</h3>", unsafe_allow_html=True)

# Sortable and filterable table
col1, col2, col3 = st.columns(3)

with col1:
    sort_by = st.selectbox("Sort by:", options=['name', 'blood_group', 'pints_donated', 'number_of_donation', 'city'])

with col2:
    ascending = st.checkbox("Ascending order", value=True)

with col3:
    display_count = st.slider("Records to display:", 5, 100, 20)

sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending).head(display_count)

# Custom dataframe display
display_cols = ['donor_id', 'name', 'blood_group', 'city', 'availability', 'number_of_donation', 'pints_donated', 'months_since_first_donation']
st.dataframe(
    sorted_df[display_cols].style.format({
        'number_of_donation': '{:.0f}',
        'pints_donated': '{:.0f}',
        'months_since_first_donation': '{:.0f}'
    }),
    use_container_width=True,
    height=400
)

st.markdown("---")

# KEY INSIGHTS
st.markdown("<h3 class='header-style'>🔍 Key Insights & Recommendations</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Most Common Blood Group**  
    {filtered_df['blood_group'].value_counts().index[0]}  
    ({filtered_df['blood_group'].value_counts().values[0]} donors)
    """)

with col2:
    st.warning(f"""
    **City with Most Donors**  
    {filtered_df['city'].value_counts().index[0]}  
    ({filtered_df['city'].value_counts().values[0]} donors)
    """)

with col3:
    st.success(f"""
    **Highest Inventory Blood Group**  
    {filtered_df.groupby('blood_group')['pints_donated'].sum().idxmax()}  
    ({filtered_df.groupby('blood_group')['pints_donated'].sum().max():.0f} pints)
    """)

# Detailed recommendations
st.markdown("""
### 💡 Strategic Recommendations:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ✅ **Recruitment Strategy**
    - Focus recruitment campaigns in cities with fewer donors
    - Target blood groups with low inventory levels
    - Implement community outreach programs
    
    ✅ **Donor Management**
    - Encourage regular donations from available donors
    - Create loyalty rewards for frequent donors
    - Schedule follow-ups for inactive donors
    """)

with col2:
    st.markdown("""
    ✅ **Inventory Management**
    - Stock up on the most demanded blood groups
    - Monitor stock levels in real-time
    - Implement emergency protocols for critical shortages
    
    ✅ **Analytics & Forecasting**
    - Use predictive analytics to forecast blood demand
    - Analyze seasonal donation patterns
    - Plan mobile donation drives strategically
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; font-size: 12px;'>
    <p>Built with Streamlit | Blood Bank Management System Dashboard | Last Updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
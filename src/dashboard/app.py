"""
Kenya Tech Landscape Dashboard
Interactive visualization of job market trends and skills analysis.

Structure:
- Page 1: What Should I Learn? (Skills focus)
- Page 2: Can I Get Hired? (Requirements focus)
- Page 3: Where Should I Apply? (Market focus)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from itertools import combinations
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Kenya Tech Landscape",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
    }
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #4361ee;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():
    """Load all processed data files."""
    base_path = Path(__file__).parent.parent.parent / "data" / "processed"
    
    jobs = pd.read_csv(base_path / "jobs_cleaned.csv")
    skills = pd.read_csv(base_path / "skills_v2.csv")
    skills_summary = pd.read_csv(base_path / "skills_summary.csv")
    cooccurrence = pd.read_csv(base_path / "skill_cooccurrence_hard_skills.csv")
    
    return jobs, skills, skills_summary, cooccurrence


# ============================================================
# SHARED COMPONENTS
# ============================================================

DOMAIN_COLORS = {
    "data_science": "#4361ee",
    "cyber_security": "#f72585",
    "web_dev": "#4cc9f0",
    "network_systems": "#7209b7",
    "other": "#adb5bd",
    "general": "#6c757d"
}

DOMAIN_LABELS = {
    "data_science": "Data Science & Analytics",
    "cyber_security": "Cybersecurity",
    "web_dev": "Web Development",
    "network_systems": "Network & Systems",
    "other": "Other / Unclassified",
    "general": "General/Soft Skills"
}

CATEGORY_COLORS = {
    "languages": "#4361ee",
    "ml_ai_frameworks": "#7209b7",
    "databases": "#3a0ca3",
    "bi_tools": "#f72585",
    "big_data": "#4895ef",
    "devops_tools": "#4cc9f0",
    "concepts": "#560bad",
    "certifications": "#f77f00",
    "tools": "#d62828",
    "frameworks": "#52b788",
    "backend_frameworks": "#2d6a4f",
    "frontend_frameworks": "#40916c",
    "soft_skills": "#adb5bd",
}


def render_header():
    """Render the main header."""
    st.markdown('<p class="main-header">🇰🇪 Kenya Tech Landscape</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive analysis of the Kenyan tech job market - skills, experience, and opportunities</p>', unsafe_allow_html=True)


def render_key_metrics(jobs_df: pd.DataFrame, skills_df: pd.DataFrame):
    """Render key metrics cards."""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Jobs", f"{len(jobs_df):,}")
    with col2:
        st.metric("Unique Skills", f"{skills_df['skill_name'].nunique():,}")
    with col3:
        st.metric("Companies", f"{jobs_df['company_clean'].nunique():,}")
    with col4:
        avg_skills = len(skills_df) / len(jobs_df)
        st.metric("Avg Skills/Job", f"{avg_skills:.1f}")
    with col5:
        entry_level_pct = (jobs_df["experience_years_min"].fillna(0) <= 2).mean() * 100
        st.metric("Entry-Level Jobs", f"{entry_level_pct:.0f}%")


# ============================================================
# PAGE 1: WHAT SHOULD I LEARN?
# ============================================================

def page_what_to_learn(skills_summary: pd.DataFrame, skills_df: pd.DataFrame, jobs_df: pd.DataFrame, cooccurrence_df: pd.DataFrame):
    """Page focused on skill selection and learning path."""
    
    st.header("🎓 What Should I Learn?")
    st.caption("Data-driven guidance for your tech learning journey")
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Top Skills",
        "🔗 Skill Pairs",
        "🔍 Skill Search"
    ])
    
    with tab1:
        view_top_skills_enhanced(skills_summary)
    
    with tab2:
        view_skill_cooccurrence_by_domain(cooccurrence_df, skills_df, jobs_df)
    
    with tab3:
        view_skill_search(skills_summary, skills_df, jobs_df)


def view_top_skills_enhanced(skills_summary: pd.DataFrame):
    """Q1: What skills should I learn first to get hired?"""
    st.subheader("Top Skills to Get Hired")
    st.caption("Skills ranked by % of jobs requiring them")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        domain_filter = st.selectbox(
            "Filter by Domain",
            ["all_hard_skills", "data_science", "web_dev", "cyber_security", "network_systems"],
            format_func=lambda x: "All Hard Skills" if x == "all_hard_skills" else DOMAIN_LABELS.get(x, x)
        )
        
        top_n = st.slider("Show top N skills", 10, 30, 15)
    
    # Filter data
    if domain_filter == "all_hard_skills":
        filtered = skills_summary[skills_summary["category"] != "soft_skills"]
    else:
        filtered = skills_summary[skills_summary["domain"] == domain_filter]
    
    top_skills = filtered.nlargest(top_n, "pct_of_total")
    
    # Create bar chart
    fig = px.bar(
        top_skills,
        x="pct_of_total",
        y="skill_name",
        orientation="h",
        color="category",
        color_discrete_map=CATEGORY_COLORS,
        text=top_skills["pct_of_total"].apply(lambda x: f"{x:.0f}%"),
        labels={
            "pct_of_total": "% of Jobs Requiring Skill",
            "skill_name": "",
            "category": "Category"
        }
    )
    
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        height=50 + top_n * 28,
        margin=dict(l=0, r=50, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    fig.update_traces(textposition="outside")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insight
    if len(top_skills) > 0:
        top = top_skills.iloc[0]
        st.info(f"💡 **{top['skill_name']}** appears in {top['pct_of_total']:.0f}% of tech jobs - consider starting here!")


def view_skill_cooccurrence_by_domain(cooccurrence_df: pd.DataFrame, skills_df: pd.DataFrame, jobs_df: pd.DataFrame):
    """Q2: If I learn X, what should I learn next? - By Domain"""
    st.subheader("Skill Co-occurrence: Learning Paths")
    st.caption("When you know skill A, what's commonly required alongside it?")
    
    # Domain filter for co-occurrence
    col1, col2a, col2b = st.columns([1, 2, 2])
    
    with col1:
        domain_filter = st.selectbox(
            "Filter pairs by domain",
            ["all", "data_science", "web_dev", "cyber_security", "network_systems"],
            format_func=lambda x: "All Domains" if x == "all" else DOMAIN_LABELS.get(x, x),
            key="cooccur_domain"
        )
    
    with col2a:
        min_count = st.slider("Minimum co-occurrence", 1, 20, 2)
    
    with col2b:
        # Skill search for "next step" analysis
        all_skills = sorted(skills_df[skills_df["category"] != "soft_skills"]["skill_name"].unique())
        selected_skill = st.selectbox(
            "I already know...",
            [""] + list(all_skills),
            format_func=lambda x: "Select a skill to see what to learn next" if x == "" else x
        )
    
    if selected_skill:
        # Show what to learn next based on selected skill
        st.markdown(f"#### If you know **{selected_skill}**, learn these next:")
        
        skill_jobs = skills_df[skills_df["skill_name"] == selected_skill]["job_id"].unique()
        related = skills_df[
            (skills_df["job_id"].isin(skill_jobs)) &
            (skills_df["skill_name"] != selected_skill) &
            (skills_df["category"] != "soft_skills")
        ]
        
        # Filter by domain if selected
        if domain_filter != "all":
            related = related[related["domain"] == domain_filter]
        
        related_counts = related["skill_name"].value_counts().head(10)
        
        if len(related_counts) > 0:
            # Calculate co-occurrence percentage
            cooccur_pct = (related_counts / len(skill_jobs) * 100).round(0)
            
            fig = px.bar(
                x=cooccur_pct.values,
                y=cooccur_pct.index,
                orientation="h",
                text=[f"{v:.0f}%" for v in cooccur_pct.values],
                color_discrete_sequence=["#4361ee"]
            )
            fig.update_layout(
                xaxis_title="% of jobs that also require this",
                yaxis_title="",
                yaxis=dict(categoryorder="total ascending"),
                height=350,
                margin=dict(l=0, r=50, t=20, b=0)
            )
            fig.update_traces(textposition="outside")
            
            st.plotly_chart(fig, use_container_width=True)
            
            top_next = cooccur_pct.index[0]
            st.success(f"🎯 **{cooccur_pct.iloc[0]:.0f}%** of {selected_skill} jobs also need **{top_next}** - learn this next!")
        else:
            st.warning("No related skills found for this filter combination")
    else:
        # Show general co-occurrence table (Dynamic calculation)
        st.markdown("#### Most Common Skill Pairs (Hard Skills)")
        
        # 1. Filter jobs by domain
        if domain_filter != "all":
            # Filter jobs first
            domain_jobs = jobs_df[jobs_df["domain"] == domain_filter]["id"]
            # Then filter skills to those jobs
            filtered_skills_df = skills_df[skills_df["job_id"].isin(domain_jobs)]
        else:
            filtered_skills_df = skills_df
            
        # 2. Filter to hard skills only
        hard_skills = filtered_skills_df[
            (filtered_skills_df["category"] != "soft_skills")
        ]
        
        # 3. Calculate pairs on the fly
        if not hard_skills.empty:
            # Group skills by job
            job_skills = hard_skills.groupby("job_id")["skill_name"].apply(list)
            
            # Count pairs
            pair_counts = Counter()
            for skills in job_skills:
                if len(skills) >= 2:
                    # Sort to ensure (A,B) is same as (B,A)
                    for pair in combinations(set(skills), 2):
                        pair_counts[tuple(sorted(pair))] += 1
                        
            # Convert to DataFrame
            if pair_counts:
                pairs_data = [
                    {"Skill 1": p[0], "Skill 2": p[1], "Times Together": c} 
                    for p, c in pair_counts.most_common(20)
                ]
                display_df = pd.DataFrame(pairs_data)
                
                # Calculate % Co-occurrence (relative to total domain jobs)
                total_domain_jobs = len(job_skills)
                display_df["% Co-occurrence"] = (display_df["Times Together"] / total_domain_jobs * 100).apply(lambda x: f"{x:.0f}%")
                
                # Filter by min count from slider
                display_df = display_df[display_df["Times Together"] >= min_count]
                
                st.dataframe(
                    display_df.style.background_gradient(subset=["Times Together"], cmap="Blues"),
                    use_container_width=True,
                    hide_index=True
                )
                
                if len(display_df) > 0:
                    top = display_df.iloc[0]
                    st.info(f"💡 **{top['Skill 1']} + {top['Skill 2']}** appear together in {top['Times Together']} {DOMAIN_LABELS.get(domain_filter, domain_filter)} jobs")
            else:
                st.warning("No skill pairs found for this domain.")
        else:
            st.warning("No data available for this filter.")


def view_skill_search(skills_summary: pd.DataFrame, skills_df: pd.DataFrame, jobs_df: pd.DataFrame):
    """Skill deep-dive search."""
    st.subheader("Skill Deep Dive")
    
    all_skills = sorted(skills_summary["skill_name"].unique())
    selected_skill = st.selectbox(
        "Search for any skill or framework",
        [""] + all_skills,
        format_func=lambda x: "Type to search..." if x == "" else x,
        key="skill_search_main"
    )
    
    if selected_skill:
        skill_info = skills_summary[skills_summary["skill_name"] == selected_skill].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Jobs Requiring This", skill_info["job_count"])
        with col2:
            st.metric("% of All Jobs", f"{skill_info['pct_of_total']}%")
        with col3:
            st.metric("Avg Min Experience", f"{skill_info['avg_exp_min']:.1f} yrs")
        with col4:
            st.metric("Category", skill_info["category"].replace("_", " ").title())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔗 Commonly Paired With")
            skill_jobs = skills_df[skills_df["skill_name"] == selected_skill]["job_id"].unique()
            related = skills_df[
                (skills_df["job_id"].isin(skill_jobs)) &
                (skills_df["skill_name"] != selected_skill) &
                (skills_df["category"] != "soft_skills")
            ]["skill_name"].value_counts().head(8)
            
            if len(related) > 0:
                fig = px.bar(
                    x=related.values,
                    y=related.index,
                    orientation="h",
                    color_discrete_sequence=["#4361ee"]
                )
                fig.update_layout(
                    xaxis_title="Co-occurrence Count",
                    yaxis_title="",
                    yaxis=dict(categoryorder="total ascending"),
                    height=280,
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📋 Sample Job Titles")
            sample_job_ids = skill_jobs[:5]
            sample_jobs = jobs_df[jobs_df["id"].isin(sample_job_ids)][["job_title_clean", "company_clean"]].copy()
            sample_jobs.columns = ["Job Title", "Company"]
            st.dataframe(sample_jobs, use_container_width=True, hide_index=True)


# ============================================================
# PAGE 2: CAN I GET HIRED?
# ============================================================

def page_can_i_get_hired(jobs_df: pd.DataFrame, skills_df: pd.DataFrame, skills_summary: pd.DataFrame):
    """Page focused on job requirements and barriers to entry."""
    
    st.header("🚀 Can I Get Hired?")
    st.caption("Understanding the barriers to entry and what employers actually want")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Experience Levels",
        "🎓 Education",
        "🚪 Domain Access",
        "💪 Competitiveness"
    ])
    
    with tab1:
        view_experience_distribution(jobs_df)
    
    with tab2:
        view_education_requirements(jobs_df)
    
    with tab3:
        view_domain_accessibility_enhanced(jobs_df)
    
    with tab4:
        view_job_competitiveness(skills_df, jobs_df)


def view_experience_distribution(jobs_df: pd.DataFrame):
    """Q5: How much experience do I need before I can get hired?"""
    st.subheader("Experience Requirements Distribution")
    st.caption("What experience levels are employers actually hiring for?")
    
    # Categorize experience levels
    def categorize_exp(row):
        min_exp = row.get("experience_years_min", 0)
        if pd.isna(min_exp):
            min_exp = 0
        if min_exp <= 1:
            return "0-1 years (Entry)"
        elif min_exp <= 3:
            return "1-3 years (Junior)"
        elif min_exp <= 5:
            return "3-5 years (Mid)"
        else:
            return "5+ years (Senior)"
    
    jobs_df["exp_category"] = jobs_df.apply(categorize_exp, axis=1)
    
    # Aggregate by experience and domain
    exp_domain = jobs_df.groupby(["exp_category", "domain"]).size().reset_index(name="count")
    
    # Order categories
    exp_order = ["0-1 years (Entry)", "1-3 years (Junior)", "3-5 years (Mid)", "5+ years (Senior)"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Simplified: Just show entry-level % by domain
        entry_level_data = []
        for domain in jobs_df["domain"].unique():
             domain_jobs = jobs_df[jobs_df["domain"] == domain]
             if len(domain_jobs) > 0:
                 entry_count = domain_jobs[domain_jobs["experience_years_min"].fillna(0) <= 2].shape[0]
                 pct = entry_count / len(domain_jobs) * 100
                 entry_level_data.append({
                     "Domain": DOMAIN_LABELS.get(domain, domain),
                     "Entry Level %": pct,
                     "color": DOMAIN_COLORS.get(domain, "#ccc")
                 })
        
        plot_df = pd.DataFrame(entry_level_data).sort_values("Entry Level %", ascending=False)
        
        fig = px.bar(
            plot_df,
            x="Entry Level %",
            y="Domain",
            orientation="h",
            text=plot_df["Entry Level %"].apply(lambda x: f"{x:.0f}%"),
            title="Percentage of Entry-Level Jobs (≤2 Years Exp)",
            color="Domain",
            color_discrete_sequence=plot_df["color"]
        )
        
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Summary stats
        exp_counts = jobs_df["exp_category"].value_counts()
        total = len(jobs_df)
        
        st.markdown("#### Quick Stats")
        for cat in exp_order:
            count = exp_counts.get(cat, 0)
            pct = count / total * 100
            st.metric(cat, f"{pct:.0f}%", f"{count} jobs")
    
    # Insight
    entry_junior = jobs_df[jobs_df["exp_category"].isin(["0-1 years (Entry)", "1-3 years (Junior)"])].shape[0]
    entry_pct = entry_junior / len(jobs_df) * 100
    st.success(f"🎯 **Good news!** {entry_pct:.0f}% of jobs require ≤3 years experience - you CAN break in!")


def view_education_requirements(jobs_df: pd.DataFrame):
    """Q6: Do I need a specific degree, or can I self-teach?"""
    st.subheader("Education Requirements")
    st.caption("What qualifications do employers actually require?")
    
    # Categorize education
    def categorize_edu(edu):
        if pd.isna(edu) or edu == "":
            return "Not Specified"
        edu_lower = str(edu).lower()
        if "master" in edu_lower or "msc" in edu_lower or "mba" in edu_lower:
            return "Master's Preferred"
        elif "bachelor" in edu_lower or "bsc" in edu_lower or "degree" in edu_lower:
            return "Bachelor's Required"
        elif "diploma" in edu_lower or "certificate" in edu_lower:
            return "Diploma/Certificate"
        else:
            return "Not Specified"
    
    jobs_df["edu_category"] = jobs_df["education_level"].apply(categorize_edu)
    
    edu_counts = jobs_df["edu_category"].value_counts()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Simplified: Degree Required vs Not Required
        def simplified_edu(cat):
            if "Bachelor" in cat or "Master" in cat:
                return "Degree Required"
            return "No Degree Specified"
        
        jobs_df["edu_simple"] = jobs_df["edu_category"].apply(simplified_edu)
        simple_counts = jobs_df["edu_simple"].value_counts()
        
        fig = px.pie(
            values=simple_counts.values,
            names=simple_counts.index,
            hole=0.5,
            title="Is a Degree Required?",
            color_discrete_sequence=["#4361ee", "#4cc9f0"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### % Jobs Not Requiring Degree by Domain")
        
        # Calculate % no degree by domain
        domain_nodegree = jobs_df.groupby("domain")["edu_simple"].apply(lambda x: (x == "No Degree Specified").mean() * 100).sort_values(ascending=False).reset_index()
        domain_nodegree["Domain Label"] = domain_nodegree["domain"].map(lambda x: DOMAIN_LABELS.get(x, x))
        
        fig2 = px.bar(
            domain_nodegree,
            x="edu_simple",
            y="Domain Label",
            orientation="h",
            text=domain_nodegree["edu_simple"].apply(lambda x: f"{x:.0f}%"),
            color="domain",
            color_discrete_map=DOMAIN_COLORS
        )
        fig2.update_layout(xaxis_title="% No Degree Specified", height=300, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Insight
    flexible_pct = (simple_counts.get("No Degree Specified", 0) / len(jobs_df) * 100)
    st.info(f"💡 {flexible_pct:.0f}% of jobs don't strictly require a degree - skills matter more!")


def view_domain_accessibility_enhanced(jobs_df: pd.DataFrame):
    """Q8 + Accessibility: Which domains are easier to break into?"""
    st.subheader("Domain Accessibility")
    st.caption("How easy is it to get started in each field?")
    
    col1, col2 = st.columns(2)
    
    # Simple Chart 1: Entry Level Availability
    with col1:
        st.markdown("**1. Entry-Level Opportunities**")
        st.write("Percentage of jobs requiring 0-2 years experience.")
        
        entry_data = []
        for domain in ["data_science", "web_dev", "cyber_security", "network_systems"]:
            jobs = jobs_df[jobs_df["domain"] == domain]
            if len(jobs) > 0:
                pct = (jobs["experience_years_min"].fillna(0) <= 2).mean() * 100
                entry_data.append({"Domain": DOMAIN_LABELS.get(domain), "Value": pct, "code": domain})
        
        df1 = pd.DataFrame(entry_data).sort_values("Value", ascending=False)
        fig1 = px.bar(df1, x="Value", y="Domain", orientation="h", text=df1["Value"].apply(lambda x: f"{x:.0f}%"), color="code", color_discrete_map=DOMAIN_COLORS)
        fig1.update_layout(height=250, xaxis_title="% Entry Level", showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    # Simple Chart 2: Education Barrier
    with col2:
        st.markdown("**2. Education Barrier**")
        st.write("Percentage of jobs that accept applicants without a degree.")
        
        edu_data = []
        for domain in ["data_science", "web_dev", "cyber_security", "network_systems"]:
            jobs = jobs_df[jobs_df["domain"] == domain]
            if len(jobs) > 0:
                # Count "Not Specified" or "Diploma" as accessible
                accessible = jobs["education_level"].apply(lambda x: pd.isna(x) or "diploma" in str(x).lower() or "certificate" in str(x).lower()).mean() * 100
                edu_data.append({"Domain": DOMAIN_LABELS.get(domain), "Value": accessible, "code": domain})
        
        df2 = pd.DataFrame(edu_data).sort_values("Value", ascending=False)
        fig2 = px.bar(df2, x="Value", y="Domain", orientation="h", text=df2["Value"].apply(lambda x: f"{x:.0f}%"), color="code", color_discrete_map=DOMAIN_COLORS)
        fig2.update_layout(height=250, xaxis_title="% No Degree Required", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.success("💡 **Interpretation:** High bars mean easier access! **Web Development** is typically the most self-taught friendly.")


def view_job_competitiveness(skills_df: pd.DataFrame, jobs_df: pd.DataFrame):
    """Q17: How competitive are these roles?"""
    st.subheader("Skill Demand Intensity")
    st.caption("Average number of hard skills required per job")
    
    # Count skills per job
    skills_per_job = skills_df[skills_df["category"] != "soft_skills"].groupby("job_id")["skill_name"].count().reset_index()
    skills_per_job.columns = ["job_id", "skill_count"]
    
    # Merge with jobs
    jobs_with_skills = jobs_df.merge(skills_per_job, left_on="id", right_on="job_id", how="left")
    jobs_with_skills["skill_count"] = jobs_with_skills["skill_count"].fillna(0)
    
    # Avg per domain
    avg_per_domain = jobs_with_skills.groupby("domain")["skill_count"].mean().sort_values().reset_index()
    avg_per_domain["Domain Label"] = avg_per_domain["domain"].map(lambda x: DOMAIN_LABELS.get(x, x))
    
    fig = px.bar(
        avg_per_domain,
        x="skill_count",
        y="Domain Label",
        orientation="h",
        color="domain",
        color_discrete_map=DOMAIN_COLORS,
        text=avg_per_domain["skill_count"].apply(lambda x: f"{x:.1f} skills"),
        title="Avg Hard Skills Required"
    )
    
    fig.update_layout(showlegend=False, xaxis_title="Avg Skills Count", height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Interpretation:** Roles requiring more skills (like Data Science) usually require deeper study before applying.")


# ============================================================
# PAGE 3: WHERE SHOULD I APPLY?
# ============================================================

def page_where_to_apply(jobs_df: pd.DataFrame, skills_summary: pd.DataFrame):
    """Page focused on job market dynamics and targeting applications."""
    
    st.header("🎯 Where Should I Apply?")
    st.caption("Strategic insights for targeting your job search")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Top Companies",
        "📊 Domain Market",
        "🌍 Location",
        "📰 Job Sources"
    ])
    
    with tab1:
        view_top_companies(jobs_df)
    
    with tab2:
        view_domain_marketability(jobs_df)
    
    with tab3:
        view_location_analysis(jobs_df)
    
    with tab4:
        view_job_sources(jobs_df)


def view_top_companies(jobs_df: pd.DataFrame):
    """Q11: Which companies are hiring the most?"""
    st.subheader("Top Hiring Companies")
    st.caption("Focus your applications on companies actively hiring in tech")
    
    # Filter out Unknown companies
    known_companies = jobs_df[jobs_df["company_clean"] != "Unknown"]
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        top_n = st.slider("Show top N companies", 10, 25, 15, key="top_companies")
        domain_filter = st.selectbox(
            "By Domain",
            ["all"] + list(jobs_df["domain"].unique()),
            format_func=lambda x: "All Domains" if x == "all" else DOMAIN_LABELS.get(x, x),
            key="company_domain"
        )
    
    # Filter and aggregate
    if domain_filter != "all":
        filtered = known_companies[known_companies["domain"] == domain_filter]
    else:
        filtered = known_companies
    
    company_counts = filtered["company_clean"].value_counts().head(top_n)
    
    with col2:
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation="h",
            text=company_counts.values,
            color_discrete_sequence=["#4361ee"]
        )
        
        fig.update_layout(
            xaxis_title="Number of Job Postings",
            yaxis_title="",
            yaxis=dict(categoryorder="total ascending"),
            height=50 + top_n * 28,
            margin=dict(l=0, r=50, t=20, b=0)
        )
        fig.update_traces(textposition="outside")
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Insight
    if len(company_counts) > 0:
        top_company = company_counts.index[0]
        top_count = company_counts.values[0]
        banks = [c for c in company_counts.index[:5] if "bank" in c.lower()]
        
        st.info(f"💡 **{top_company}** leads with {top_count} openings. " + 
                (f"Banks dominate the top 5!" if len(banks) >= 2 else ""))


def view_domain_marketability(jobs_df: pd.DataFrame):
    """Q8: Domain comparison - market overview."""
    st.subheader("Domain Market Overview")
    st.caption("Which tech domains have the most opportunities?")
    
    domain_stats = jobs_df.groupby("domain").agg(
        job_count=("id", "count"),
        avg_exp_min=("experience_years_min", "mean"),
        internship_rate=("is_internship", "mean")
    ).reset_index()
    
    domain_stats["label"] = domain_stats["domain"].map(DOMAIN_LABELS)
    domain_stats["pct"] = (domain_stats["job_count"] / domain_stats["job_count"].sum() * 100).round(1)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Bar chart
        fig = px.bar(
            domain_stats.sort_values("job_count", ascending=True),
            x="job_count",
            y="label",
            orientation="h",
            color="domain",
            color_discrete_map=DOMAIN_COLORS,
            text=domain_stats.sort_values("job_count", ascending=True)["pct"].apply(lambda x: f"{x:.0f}%")
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_title="Number of Jobs",
            yaxis_title="",
            height=300,
            margin=dict(l=0, r=50, t=20, b=0)
        )
        fig.update_traces(textposition="outside")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Summary table
        st.markdown("#### Domain Comparison")
        
        display = domain_stats[["label", "job_count", "pct", "avg_exp_min"]].copy()
        display.columns = ["Domain", "Jobs", "Market Share", "Avg Exp Required"]
        display["Market Share"] = display["Market Share"].apply(lambda x: f"{x:.0f}%")
        display["Avg Exp Required"] = display["Avg Exp Required"].apply(lambda x: f"{x:.1f} yrs")
        display = display.sort_values("Jobs", ascending=False)
        
        st.dataframe(display, use_container_width=True, hide_index=True)
    
    top = domain_stats.loc[domain_stats["job_count"].idxmax()]
    st.success(f"🎯 **{top['label']}** dominates with {top['pct']:.0f}% market share ({top['job_count']} jobs)")


def view_location_analysis(jobs_df: pd.DataFrame):
    """Q12: Are most jobs remote or on-site?"""
    st.subheader("Location & Remote Work")
    st.caption("Understanding where you'll need to be")
    
    location_counts = jobs_df["location_clean"].value_counts()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig = px.pie(
            values=location_counts.values,
            names=location_counts.index,
            hole=0.4,
            color_discrete_sequence=["#4361ee", "#f72585", "#4cc9f0", "#adb5bd"]
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### By Domain")
        
        # Check for remote/hybrid in jobs
        jobs_df["work_type"] = jobs_df["location_clean"].apply(
            lambda x: "Remote" if x == "Remote" else ("Hybrid" if x == "Hybrid" else "On-site")
        )
        
        work_domain = pd.crosstab(jobs_df["domain"], jobs_df["work_type"], normalize="index") * 100
        work_domain = work_domain.round(0).astype(int).astype(str) + "%"
        work_domain.index = work_domain.index.map(lambda x: DOMAIN_LABELS.get(x, x))
        
        st.dataframe(work_domain, use_container_width=True)
    
    nairobi_pct = location_counts.get("Nairobi", 0) / len(jobs_df) * 100
    st.info(f"📍 {nairobi_pct:.0f}% of jobs are based in Nairobi - Kenya's tech hub")


def view_job_sources(jobs_df: pd.DataFrame):
    """Q20: Which job boards have the best opportunities?"""
    st.subheader("Job Sources Comparison")
    st.caption("Where to find the best opportunities")
    
    source_domain = jobs_df.groupby(["source", "domain"]).size().reset_index(name="count")
    
    fig = px.bar(
        source_domain,
        x="source",
        y="count",
        color="domain",
        color_discrete_map=DOMAIN_COLORS,
        barmode="group",
        labels={"source": "Job Source", "count": "Number of Jobs", "domain": "Domain"}
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    fig.for_each_trace(lambda t: t.update(name=DOMAIN_LABELS.get(t.name, t.name)))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top source per domain
    best_source = source_domain.loc[source_domain.groupby("domain")["count"].idxmax()]
    
    st.markdown("#### Best Source by Domain")
    for _, row in best_source.iterrows():
        st.write(f"- **{DOMAIN_LABELS.get(row['domain'], row['domain'])}**: {row['source']} ({row['count']} jobs)")


# ============================================================
# PAGE 4: SOFT SKILLS (BONUS)
# ============================================================

def view_soft_skills(skills_summary: pd.DataFrame):
    """Q18: What soft skills do employers actually care about?"""
    st.subheader("Most Valued Soft Skills")
    st.caption("Beyond technical skills - what employers look for")
    
    soft = skills_summary[skills_summary["category"] == "soft_skills"].nlargest(15, "job_count")
    
    fig = px.bar(
        soft,
        x="pct_of_total",
        y="skill_name",
        orientation="h",
        text=soft["pct_of_total"].apply(lambda x: f"{x:.0f}%"),
        color_discrete_sequence=["#7209b7"]
    )
    
    fig.update_layout(
        xaxis_title="% of Jobs Mentioning This",
        yaxis_title="",
        yaxis=dict(categoryorder="total ascending"),
        height=450,
        margin=dict(l=0, r=50, t=20, b=0)
    )
    fig.update_traces(textposition="outside")
    
    st.plotly_chart(fig, use_container_width=True)
    
    top = soft.iloc[0]
    st.info(f"💡 **{top['skill_name'].title()}** appears in {top['pct_of_total']:.0f}% of jobs - practice this!")


# ============================================================
# MAIN APP
# ============================================================

def main():
    """Main dashboard entry point."""
    # Load data
    try:
        jobs_df, skills_df, skills_summary, cooccurrence_df = load_data()
    except FileNotFoundError as e:
        st.error(f"Data files not found. Please run the data processing scripts first.\n\nError: {e}")
        return
    
    # Render header
    render_header()
    
    # Key metrics
    render_key_metrics(jobs_df, skills_df)
    
    st.divider()
    
    # Main navigation (3 pages)
    page = st.radio(
        "Navigate",
        ["🎓 What Should I Learn?", "🚀 Can I Get Hired?", "🎯 Where Should I Apply?", "💬 Soft Skills"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if page == "🎓 What Should I Learn?":
        page_what_to_learn(skills_summary, skills_df, jobs_df, cooccurrence_df)
    elif page == "🚀 Can I Get Hired?":
        page_can_i_get_hired(jobs_df, skills_df, skills_summary)
    elif page == "🎯 Where Should I Apply?":
        page_where_to_apply(jobs_df, skills_summary)
    elif page == "💬 Soft Skills":
        view_soft_skills(skills_summary)
    
    # Footer
    st.divider()
    st.caption("Data source: BrighterMonday, MyJobMag, OYK | Last updated: Feb 2026")


if __name__ == "__main__":
    main()

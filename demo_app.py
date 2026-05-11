import streamlit as st
from rfp_processor_v3 import RFPProcessorV3
import os
from datetime import datetime
from sheets_tracker import SheetsTracker
from quality_visualizer import display_quality_score, display_stats_dashboard
from smart_suggestions import analyze_rfp_and_suggest, display_suggestions

# Page config
st.set_page_config(
    page_title="Vela AI - RFP Intelligence Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .info-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_processor():
    return RFPProcessorV3()

@st.cache_resource
def get_tracker():
    return SheetsTracker()

processor = get_processor()
tracker = get_tracker()

# Header
st.markdown('<h1 class="main-header">⚡ Vela AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Proposal Generation in Minutes, Not Hours</p>', unsafe_allow_html=True)

# Display dashboard stats if available
stats = tracker.get_stats()
if stats and stats.get("total_rfps", 0) > 0:
    display_stats_dashboard(stats)
    st.markdown("---")

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Upload RFP Document")
    
    # Form inputs
    project_name = st.text_input(
        "RFP/Project Name",
        placeholder="e.g., Downtown Office Renovation",
        help="Enter the name of the project from the RFP"
    )
    
    client_name = st.text_input(
        "Client Name",
        placeholder="e.g., ABC Construction",
        help="Enter the client or issuing organization name"
    )
    
    client_email = st.text_input(
        "Client Email (for delivery)",
        placeholder="e.g., john@abc.com",
        help="Enter a valid email address to receive the proposal"
    )
    
    uploaded_file = st.file_uploader(
        "Upload RFP PDF",
        type=['pdf', 'txt'],
        help="Upload your RFP document (PDF or TXT format, max 200MB)"
    )

with col2:
    st.markdown("### How It Works")
    st.markdown("""
    1. **Upload** your RFP document
    2. **AI analyzes** requirements
    3. **Generates** customized response
    4. **Review** and submit
    
    ⏱️ **Average Time:** 2-3 minutes  
    📝 **Manual Time:** 8-15 hours  
    💰 **You save:** 95% of your time
    """)
    
    st.markdown("### 🎉 Free Trial")
    st.info("Test Vela AI with your first RFP completely free!")

# Generate button
if st.button("⚡ Generate Response", type="primary", use_container_width=True):
    if not project_name:
        st.error("❌ Please enter a project name")
    elif not client_name:
        st.error("❌ Please enter a client name")
    elif not client_email:
        st.error("❌ Please enter a client email")
    elif not uploaded_file:
        st.error("❌ Please upload an RFP document")
    else:
        with st.spinner("🤖 Analyzing RFP with AI intelligence..."):
            try:
                # Save uploaded file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"data/uploads/{timestamp}_{uploaded_file.name}"
                os.makedirs("data/uploads", exist_ok=True)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Step 1: Analyze RFP
                st.info("📊 Step 1/3: Analyzing RFP requirements...")
                analysis = processor.analyze_requirements(file_path)
                
                # Read RFP text for suggestions
                if file_path.endswith('.pdf'):
                    rfp_text = processor.extract_text_from_pdf(file_path)
                else:
                    with open(file_path, 'r') as f:
                        rfp_text = f.read()
                
                # Generate smart suggestions
                suggestions = analyze_rfp_and_suggest(rfp_text[:5000], analysis)
                
                if suggestions:
                    st.markdown("---")
                    display_suggestions(suggestions)
                    st.markdown("---")
                
                # Step 2: Research with Google
                st.info("🔍 Step 2/3: Researching market intelligence...")
                response = processor.generate_response_with_research(
                    analysis,
                    project_name=project_name,
                    client_name=client_name
                )
                
                # Step 3: Score proposal
                st.info("🎯 Step 3/3: Scoring proposal quality...")
                score = processor.score_proposal(response)
                
                # Display success
                st.success("✅ Proposal generated successfully!")
                
                # Display quality score with visualizations
                with st.expander("📊 Proposal Quality Score", expanded=True):
                    display_quality_score(score)
                
                # Show preview
                with st.expander("📄 View Generated Proposal", expanded=False):
                    st.markdown(response)
                
                # Send email
                email_sent = False
                try:
                    processor.send_email_response(
                        client_email,
                        project_name,
                        response
                    )
                    st.success(f"📧 Proposal sent to {client_email}")
                    email_sent = True
                except Exception as e:
                    st.warning(f"⚠️ Proposal generated but email failed: {str(e)}")
                    st.info("💡 You can copy the proposal above and send it manually")
                
                # Log to Google Sheets
                try:
                    # Extract quality score number
                    import re
                    score_match = re.search(r'SCORE:\s*(\d+\.?\d*)/10', score)
                    quality_score = float(score_match.group(1)) if score_match else None
                    
                    tracker.log_rfp(
                        project_name=project_name,
                        client_name=client_name,
                        quality_score=quality_score,
                        email_sent=email_sent,
                        proposal_generated=True
                    )
                except Exception as e:
                    # Silently fail if tracking doesn't work
                    pass
                
                # Download button
                st.download_button(
                    label="⬇️ Download Proposal",
                    data=response,
                    file_name=f"{project_name.replace(' ', '_')}_proposal.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating proposal: {str(e)}")
                st.info("💡 Please check your configuration and try again")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666;">Powered by AVIKSOFT LLC | Questions? Email: <a href="mailto:sandeep@aviksoft.com">sandeep@aviksoft.com</a></p>',
    unsafe_allow_html=True
)

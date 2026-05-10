import streamlit as st
from rfp_processor_v2 import RFPProcessor
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Vela AI - RFP Intelligence Engine",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #00d9ff 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #a0aec0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize processor
@st.cache_resource
def get_processor():
    return RFPProcessorV3()

processor = get_processor()

# Header
st.markdown('<h1 class="main-header">⚡ Vela AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Proposal Generation in Minutes, Not Hours</p>', unsafe_allow_html=True)

# Two column layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Upload RFP Document")
    
    # Project details
    project_name = st.text_input(
        "RFP/Project Name",
        placeholder="e.g., Downtown Office Renovation"
    )
    
    client_name = st.text_input(
        "Client Name",
        placeholder="e.g., ABC Construction"
    )
    
    client_email = st.text_input(
        "Client Email (for delivery)",
        placeholder="e.g., john@abc.com"
    )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload RFP PDF",
        type=['pdf', 'txt'],
        help="Upload the RFP document to analyze"
    )
    
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
                
                # Process RFP with research
                st.info("📊 Step 1/3: Analyzing RFP requirements...")
                analysis = processor.analyze_requirements(file_path)
                
                st.info("🔍 Step 2/3: Researching market intelligence...")
                response = processor.generate_response_with_research(
                    analysis,
                    project_name=project_name,
                    client_name=client_name
                )
                
                st.info("🎯 Step 3/3: Scoring proposal quality...")
                score = processor.score_proposal(response)
                
                # Display success
                st.success("✅ Proposal generated successfully!")
                
                # Show quality score
                with st.expander("📊 Proposal Quality Score", expanded=True):
                    st.markdown(score)
                
                # Show preview
                with st.expander("📄 View Generated Proposal", expanded=False):
                    st.markdown(response)
                
                # Send email
                try:
                    processor.send_email_response(
                        client_email,
                        project_name,
                        response
                    )
                    st.success(f"📧 Proposal sent to {client_email}")
                except Exception as e:
                    st.warning(f"⚠️ Proposal generated but email failed: {str(e)}")
                    st.info("💡 You can copy the proposal above and send it manually")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Proposal",
                    data=response,
                    file_name=f"{project_name.replace(' ', '_')}_proposal.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating proposal: {str(e)}")
                st.info("💡 Please check your configuration")
with col2:
    st.header("How It Works")
    
    st.markdown("""
    1. **Upload** your RFP document
    2. **AI analyzes** requirements
    3. **Generates** customized response
    4. **Review** and submit
    
    ---
    
    ⏱️ **Average Time:** 2-3 minutes  
    📝 **Manual Time:** 8-15 hours  
    💰 **You save:** 95% of your time
    """)
    
    st.divider()
    
    st.info("""
    **🎉 Free Trial**
    
    Test Vela AI with your first RFP completely free!
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #a0aec0; padding: 2rem 0;'>
    Powered by <strong>AVIKSOFT LLC</strong> | 
    Questions? Email: <a href='mailto:sandeep@aviksoft.com'>sandeep@aviksoft.com</a>
</div>
""", unsafe_allow_html=True)


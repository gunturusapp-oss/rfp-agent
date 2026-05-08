"""
Vela AI - RFP Intelligence Engine
Client-facing demo application
"""

import streamlit as st
from rfp_processor_v2 import RFPProcessor
from client_database import ClientDatabase
import os

# Page config
st.set_page_config(
    page_title="Vela AI - RFP Intelligence Engine",
    page_icon="⚡",
    layout="wide"
)

# Initialize database
database = ClientDatabase()

# Initialize RFP processor
processor = RFPProcessor()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d9ff 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .tagline {
        font-size: 1.2rem;
        color: #888;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'processor' not in st.session_state:
    st.session_state.processor = RFPProcessor()
    st.session_state.db = ClientDatabase()

# Header
st.markdown('<h1 class="main-header">⚡ Vela AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">AI-Powered Proposal Generation in Minutes, Not Hours</p>', unsafe_allow_html=True)

# Sidebar - Client Management
with st.sidebar:
    st.header("Client Portal")
    
    # Add Client Form
    st.subheader("➕ Add New Client")
    with st.form("add_client_form"):
        new_client_name = st.text_input("Client Name", placeholder="ABC Construction")
        new_client_email = st.text_input("Contact Email", placeholder="john@abc.com")
        submit_client = st.form_submit_button("Add Client")
        
        if submit_client:
            if new_client_name and new_client_email:
                try:
                    database.add_client(new_client_name, new_client_email)
                    st.success(f"✅ Added {new_client_name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding client: {str(e)}")
            else:
                st.error("Please fill in both fields")
    
    st.divider()

# Client selection
st.subheader("Select Client")
try:
    clients = database.get_all_clients()
    if clients:
        client_options = {client['name']: client['id'] for client in clients}
        selected_client = st.selectbox(
            "Choose client for this proposal",
            options=list(client_options.keys())
        )
        selected_client_id = client_options[selected_client] if selected_client else None
    else:
        st.info("👆 Add a client in the sidebar first!")
        selected_client_id = None
except:
    st.warning("No clients available. Add one in the sidebar!")
    selected_client_id = None
    
# Main area
st.header("Upload RFP Document")

col1, col2 = st.columns([2, 1])

with col1:
    rfp_name = st.text_input(
        "RFP/Project Name",
        placeholder="e.g., Downtown Office Renovation"
    )
    
    uploaded_file = st.file_uploader(
        "Upload RFP PDF",
        type=['pdf', 'txt'],
        help="Upload the RFP document you want us to respond to"
    )
    
    if st.button("⚡ Generate Response", type="primary", disabled=not uploaded_file):
        if selected_client_id and rfp_name:
            with st.spinner("Processing RFP... This takes 2-3 minutes"):
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    output_path = st.session_state.processor.process_rfp(
                        client_id=selected_client_id,
                        rfp_file_path=temp_path,
                        rfp_name=rfp_name
                    )
                    
                    st.success("✅ RFP Response Generated!")
                    
                    with open(output_path, 'r') as f:
                        response_text = f.read()
                    
                    st.download_button(
                        label="📥 Download Response",
                        data=response_text,
                        file_name=f"{rfp_name}_response.txt",
                        mime="text/plain"
                    )
                    
                    with st.expander("Preview Response"):
                        st.text_area("Generated Response", response_text, height=400)
                
                except Exception as e:
                    st.error(f"Error processing RFP: {str(e)}")
                
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
            st.warning("Please enter an RFP name and select a client")

with col2:
    st.markdown("### How It Works")
    st.markdown("""
    1. **Upload** your RFP document
    2. **AI analyzes** requirements
    3. **Generates** customized response
    4. **Review** and submit
    
    **Average Time:** 2-3 minutes  
    **Manual Time:** 8-15 hours
    
    **You save:** 95% of your time
    """)

# Stats
if selected_client_id:
    st.header("📊 Your Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("RFPs Processed", client['rfps_processed'])
    
    with col2:
        st.metric("Blogs Published", client['blogs_written'])
    
    with col3:
        st.metric("Leads Generated", client['leads_generated'])

# Footer
st.markdown("---")
st.markdown("**Powered by AVIKSOFT LLC** | Questions? Email: sandeep@aviksoft.com")

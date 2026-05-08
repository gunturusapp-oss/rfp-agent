import google.generativeai as genai
import streamlit as st
from PyPDF2 import PdfReader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class RFPProcessor:
def __init__(self):
    """Initialize with Gemini 2.5 Pro (stable production model)"""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in secrets")
    
    genai.configure(api_key=api_key)
    
    # Use stable Gemini 2.5 Pro for both analysis and generation
    self.analysis_model = genai.GenerativeModel('gemini-2.5-pro')
    self.generation_model = genai.GenerativeModel('gemini-2.5-pro')

def analyze_requirements(self, file_path):
    """Analyze RFP requirements using DEEP RESEARCH"""
    # Extract text
    if file_path.endswith('.pdf'):
        rfp_text = self.extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r') as f:
            rfp_text = f.read()
    
    # Use DEEP RESEARCH model for comprehensive analysis
    prompt = f"""
    Perform a COMPREHENSIVE deep research analysis of this RFP document:
    
    {rfp_text[:30000]}
    
    Provide an in-depth analysis including:
    
    1. PROJECT UNDERSTANDING
    - Full scope and objectives
    - Industry context and trends
    - Client's strategic goals
    
    2. DETAILED REQUIREMENTS
    - Technical specifications
    - Deliverables and milestones
    - Compliance and standards
    - Hidden requirements (read between the lines)
    
    3. COMPETITIVE LANDSCAPE
    - Likely competitors for this RFP
    - What they'll propose
    - Our differentiation opportunities
    
    4. EVALUATION CRITERIA ANALYSIS
    - How proposals will be scored
    - Weighted factors
    - Winning strategies
    
    5. RISK ASSESSMENT
    - Project risks
    - Client concerns
    - Mitigation strategies
    
    6. MARKET INTELLIGENCE
    - Industry benchmarks
    - Typical pricing for similar projects
    - Success factors
    
    7. STRATEGIC RECOMMENDATIONS
    - Key win themes
    - Proposal positioning
    - Unique value propositions
    
    Be thorough, strategic, and research-backed.
    """
    
    # Use the DEEP RESEARCH model
    response = self.analysis_model.generate_content(prompt)
    return response.text

def generate_response(self, analysis, project_name, client_name):
    """Generate proposal using Gemini 3.1 Pro"""
    company_name = st.secrets.get("COMPANY_NAME", "AVIKSOFT LLC")
    company_address = st.secrets.get("COMPANY_ADDRESS", "1819 E Southern Ave, Suite D-20, Mesa, AZ 85204")
    
    prompt = f"""
    You are writing a WORLD-CLASS RFP response proposal for {company_name}.
    
    PROJECT: {project_name}
    CLIENT: {client_name}
    
    DEEP RESEARCH ANALYSIS:
    {analysis}
    
    Create a comprehensive, strategically-positioned, WINNING proposal with:
    
    # EXECUTIVE SUMMARY
    - Compelling value proposition that addresses client's strategic goals
    - Why we're uniquely positioned to succeed
    - Key differentiators (2-3 powerful paragraphs)
    
    # UNDERSTANDING & APPROACH
    - Demonstrate deep comprehension of requirements
    - Show we understand their business challenges
    - Our strategic approach and methodology
    
    # PROPOSED SOLUTION
    - Detailed technical approach
    - Implementation timeline with milestones
    - Quality assurance and risk mitigation
    - Innovation and competitive advantages
    
    # QUALIFICATIONS & EXPERIENCE
    - Our expertise in construction management and SAP systems
    - Relevant past projects and success metrics
    - Team credentials and capabilities
    - Why our experience matters for THIS project
    
    # PROJECT MANAGEMENT
    - Communication strategy
    - Risk management framework
    - Change control process
    - Success metrics and KPIs
    
    # VALUE PROPOSITION
    - ROI and business impact
    - Cost-benefit analysis
    - Long-term partnership value
    - Unique competitive advantages
    
    # TIMELINE & DELIVERABLES
    - Detailed project schedule
    - Key milestones and checkpoints
    - Quality gates and review points
    
    # WHY CHOOSE {company_name}
    - Strategic differentiators
    - Client success stories with metrics
    - Commitment and guarantees
    
    # NEXT STEPS
    - Clear call to action
    - Proposed meeting structure
    - Contact information
    
    REQUIREMENTS:
    - Professional, confident tone
    - Specific and data-driven (not generic)
    - Address ALL evaluation criteria from analysis
    - Incorporate competitive intelligence
    - Show deep understanding of their business
    - Use metrics and concrete examples
    - Make it WINNING and PERSUASIVE
    
    Close professionally:
    
    We look forward to partnering with you on this transformative project.
    
    Best regards,
    {company_name}
    {company_address}
    sandeep@aviksoft.com
    """
    
    # Use Gemini 3.1 Pro for generation
    response = self.generation_model.generate_content(prompt)
    return response.text    
    def send_email_response(self, recipient_email, project_name, proposal_text):
        """Send the proposal via email"""
        try:
            sender_email = st.secrets.get("GMAIL_USER")
            sender_password = st.secrets.get("GMAIL_APP_PASSWORD")
            
            if not sender_email or not sender_password:
                raise ValueError("Email credentials not configured")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Proposal for {project_name}"
            
            # Email body
            body = f"""
Dear Client,

Please find attached our proposal for {project_name}.

We've carefully reviewed the RFP requirements and are excited about the opportunity to work with you on this project.

{proposal_text}

We look forward to discussing this proposal with you.

Best regards,
Vela AI Team
AVIKSOFT LLC
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
                
        except Exception as e:
            raise Exception(f"Email sending failed: {str(e)}")

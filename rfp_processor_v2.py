cd ~/rfp-agent
cat > rfp_processor_v2.py << 'EOF'
import google.generativeai as genai
import streamlit as st
from PyPDF2 import PdfReader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class RFPProcessor:
    def __init__(self):
        """Initialize the RFP Processor with Gemini 2.5 Pro"""
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in secrets")
        
        genai.configure(api_key=api_key)
        
        # Use stable Gemini 2.5 Pro for both analysis and generation
        self.analysis_model = genai.GenerativeModel('gemini-2.5-pro')
        self.generation_model = genai.GenerativeModel('gemini-2.5-pro')
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def analyze_requirements(self, file_path):
        """Analyze RFP requirements using Gemini"""
        # Extract text
        if file_path.endswith('.pdf'):
            rfp_text = self.extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r') as f:
                rfp_text = f.read()
        
        # Analyze with Gemini
        prompt = f"""
        Analyze this RFP document comprehensively:
        
        {rfp_text[:30000]}
        
        Provide a detailed analysis including:
        
        1. PROJECT OVERVIEW
        - Scope and objectives
        - Industry and sector
        - Location and timeline
        
        2. KEY REQUIREMENTS
        - Technical specifications
        - Deliverables and milestones
        - Compliance requirements
        
        3. EVALUATION CRITERIA
        - How proposals will be scored
        - Decision factors
        - Priority areas
        
        4. BUDGET & TIMELINE
        - Budget constraints (if mentioned)
        - Critical deadlines
        - Payment terms
        
        5. STRATEGIC INSIGHTS
        - Client pain points
        - Competitive opportunities
        - Win themes
        
        Be thorough and specific. Extract key details.
        """
        
        response = self.analysis_model.generate_content(prompt)
        return response.text
    
    def generate_response(self, analysis, project_name, client_name):
        """Generate a professional RFP response"""
        company_name = st.secrets.get("COMPANY_NAME", "AVIKSOFT LLC")
        company_address = st.secrets.get("COMPANY_ADDRESS", "1819 E Southern Ave, Suite D-20, Mesa, AZ 85204")
        
        prompt = f"""
        You are writing a world-class RFP response proposal for {company_name}.
        
        PROJECT: {project_name}
        CLIENT: {client_name}
        
        RFP ANALYSIS:
        {analysis}
        
        Create a comprehensive, winning proposal with these sections:
        
        # EXECUTIVE SUMMARY
        - Compelling overview that captures attention
        - Clear value proposition
        - Why we're the best choice (2-3 powerful paragraphs)
        
        # UNDERSTANDING OF REQUIREMENTS
        - Demonstrate deep comprehension
        - Address each key requirement specifically
        - Show we understand their business
        
        # PROPOSED SOLUTION
        - Detailed methodology and approach
        - Implementation timeline with milestones
        - Technical specifications and deliverables
        - Quality assurance processes
        
        # QUALIFICATIONS & EXPERIENCE
        - Our expertise in construction management and technology
        - SAP EWM and supply chain optimization experience
        - Relevant past projects with success metrics
        - Team credentials and capabilities
        
        # PROJECT MANAGEMENT APPROACH
        - Communication plan
        - Risk management
        - Change control process
        - Success metrics and KPIs
        
        # VALUE PROPOSITION
        - ROI and business impact
        - Cost-benefit analysis
        - Competitive advantages
        - Long-term partnership value
        
        # TIMELINE & DELIVERABLES
        - Detailed project schedule
        - Key milestones and checkpoints
        - Quality gates and delivery commitments
        
        # WHY CHOOSE US
        - Unique competitive advantages
        - Client success stories
        - Guarantee and support commitments
        
        # NEXT STEPS
        - Clear call to action
        - Proposed meeting or discussion
        - Contact information
        
        REQUIREMENTS:
        - Professional business tone
        - Specific and detailed (not generic)
        - Address client's pain points
        - Show expertise and confidence
        - Include metrics and data where possible
        - Make it persuasive and compelling
        
        Sign off professionally:
        
        Best regards,
        {company_name}
        {company_address}
        sandeep@aviksoft.com
        
        Make this a WINNING proposal!
        """
        
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
            msg['Subject'] = f"Proposal for {project_name} - AVIKSOFT LLC"
            
            # Email body
            body = f"""
Dear Client,

Thank you for the opportunity to submit our proposal for {project_name}.

We've carefully reviewed your RFP requirements and have developed a comprehensive solution tailored to your specific needs.

{proposal_text}

We're excited about the opportunity to work with you and are confident we can deliver exceptional results.

Please let us know if you have any questions or would like to schedule a discussion.

Best regards,
Vela AI Team
AVIKSOFT LLC
1819 E Southern Ave, Suite D-20
Mesa, AZ 85204
sandeep@aviksoft.com
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
                
        except Exception as e:
            raise Exception(f"Email sending failed: {str(e)}")
EOF

import google.generativeai as genai
import streamlit as st
from PyPDF2 import PdfReader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class RFPProcessor:
    def __init__(self):
        """Initialize the RFP Processor with Gemini API"""
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in secrets")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        Analyze this RFP document and extract key requirements:
        
        {rfp_text[:8000]}  # Limit to avoid token limits
        
        Provide a structured analysis of:
        1. Project scope and objectives
        2. Key requirements and deliverables
        3. Timeline and deadlines
        4. Budget constraints (if mentioned)
        5. Evaluation criteria
        
        Be concise and focus on the most important details.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_response(self, analysis, project_name, client_name):
        """Generate a professional RFP response"""
        company_name = st.secrets.get("COMPANY_NAME", "AVIKSOFT LLC")
        company_address = st.secrets.get("COMPANY_ADDRESS", "1819 E Southern Ave, Suite D-20, Mesa, AZ 85204")
        
        prompt = f"""
        You are writing a professional RFP response proposal for {company_name}.
        
        Project: {project_name}
        Client: {client_name}
        
        Based on this RFP analysis:
        {analysis}
        
        Write a compelling, professional proposal that includes:
        
        1. EXECUTIVE SUMMARY
        - Brief overview of our understanding and proposed solution
        
        2. UNDERSTANDING OF REQUIREMENTS
        - Demonstrate clear comprehension of project needs
        
        3. PROPOSED APPROACH
        - Detailed methodology and implementation plan
        - Timeline and milestones
        
        4. QUALIFICATIONS
        - Our expertise in construction management and SAP systems
        - Relevant experience with similar projects
        
        5. VALUE PROPOSITION
        - Why we're the best choice
        - Competitive advantages
        
        6. NEXT STEPS
        - Clear call to action
        
        Make it professional, persuasive, and tailored to the client's needs.
        Use proper business formatting with clear sections.
        
        Sign off as:
        {company_name}
        {company_address}
        """
        
        response = self.model.generate_content(prompt)
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

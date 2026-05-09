import google.generativeai as genai
import streamlit as st
from PyPDF2 import PdfReader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class RFPProcessor:
    def __init__(self):
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def analyze_requirements(self, file_path):
        if file_path.endswith('.pdf'):
            rfp_text = self.extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r') as f:
                rfp_text = f.read()
        
        prompt = f"""Analyze this RFP document:
        
        {rfp_text[:20000]}
        
        Provide detailed analysis:
        1. Project scope and objectives
        2. Key requirements and deliverables
        3. Timeline and deadlines
        4. Evaluation criteria
        5. Strategic insights
        
        Be specific and thorough."""
        
        response = self.model.generate_content(prompt)
        return response.text
    
def generate_response(self, analysis, project_name, client_name):
    company = st.secrets.get("COMPANY_NAME", "AVIKSOFT LLC")
    address = st.secrets.get("COMPANY_ADDRESS", "1819 E Southern Ave, Mesa, AZ 85204")
    
    prompt = f"""Write a comprehensive winning RFP proposal for {company}.
    
    PROJECT: {project_name}
    CLIENT: {client_name}
    
    RFP ANALYSIS:
    {analysis}
    
    Create a professional proposal with these sections:
    1. Executive Summary
    2. Understanding of Requirements
    3. Proposed Solution with timeline
    4. Qualifications and Experience
    5. Value Proposition
    6. Why Choose Us
    7. Next Steps
    
    Make it persuasive and professional.
    
    CRITICAL: You MUST end with this EXACT text (copy it exactly):
    
    Best regards,
    
    AVIKSOFT LLC
    1819 E Southern Ave, Suite D-20
    Mesa, AZ 85204
    sandeep@aviksoft.com
    
    DO NOT modify the signature. Include it EXACTLY as shown above."""
    
    response = self.model.generate_content(prompt)
    
    # Add signature if Gemini forgot it
    if "sandeep@aviksoft.com" not in response.text:
        response_text = response.text.strip()
        if not response_text.endswith("Best regards,"):
            response_text += "\n\nBest regards,"
        response_text += f"""

AVIKSOFT LLC
1819 E Southern Ave, Suite D-20
Mesa, AZ 85204
sandeep@aviksoft.com"""
        return response_text
    
    return response.text

def send_email_response(self, recipient_email, project_name, proposal_text):
    try:
        sender = st.secrets.get("GMAIL_USER")
        password = st.secrets.get("GMAIL_APP_PASSWORD")
    
        if not sender or not password:
            raise ValueError("Email credentials not configured")
    
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient_email
        msg['Subject'] = f"Proposal for {project_name} - AVIKSOFT LLC"

        # Simple wrapper - proposal already has signature
        body = f"""Dear Client,

Thank you for the opportunity to submit our proposal for {project_name}.

{proposal_text}"""

        msg.attach(MIMEText(body, 'plain'))
    
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)

    except Exception as e:
        raise Exception(f"Email failed: {str(e)}")

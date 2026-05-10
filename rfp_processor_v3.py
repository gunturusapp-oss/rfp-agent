import google.generativeai as genai
import streamlit as st
from PyPDF2 import PdfReader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from googlesearch import search
import requests
from bs4 import BeautifulSoup

class RFPProcessorV3:
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
    
    def research_with_google(self, query, max_results=3):
        """Research using Google Search"""
        try:
            results = []
            for url in search(query, num_results=max_results, lang="en"):
                try:
                    # Get page content
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title and snippet
                    title = soup.find('title')
                    title_text = title.get_text() if title else url
                    
                    # Get first paragraph or meta description
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    snippet = meta_desc['content'] if meta_desc else ""
                    
                    results.append({
                        'title': title_text,
                        'url': url,
                        'snippet': snippet[:200]
                    })
                except:
                    continue
            
            return results
        except Exception as e:
            st.warning(f"Search unavailable: {str(e)}")
            return []
    
    def analyze_requirements(self, file_path):
        if file_path.endswith('.pdf'):
            rfp_text = self.extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r') as f:
                rfp_text = f.read()
        
        prompt = f"""Analyze this RFP document:
        
        {rfp_text[:20000]}
        
        Extract and provide:
        1. Project scope and objectives
        2. Key requirements and deliverables
        3. Timeline and deadlines
        4. Evaluation criteria
        5. Strategic insights
        6. Industry/sector information
        
        Be specific and thorough."""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_response_with_research(self, analysis, project_name, client_name, industry="construction"):
        """Generate proposal with competitive intelligence"""
        company = st.secrets.get("COMPANY_NAME", "AVIKSOFT LLC")
        address = st.secrets.get("COMPANY_ADDRESS", "1819 E Southern Ave, Mesa, AZ 85204")
        
        # Research competitors and market trends
        with st.status("🔍 Researching market intelligence...", expanded=True) as status:
            st.write("Analyzing competitors...")
            competitor_research = self.research_with_google(
                f"{industry} contractors Arizona trends 2026",
                max_results=3
            )
            
            st.write("Gathering industry insights...")
            market_research = self.research_with_google(
                f"{project_name} best practices {industry}",
                max_results=2
            )
            
            status.update(label="✅ Research complete!", state="complete")
        
        # Build research context
        research_context = "\n\n**MARKET INTELLIGENCE:**\n"
        if competitor_research:
            research_context += "Recent Industry Trends:\n"
            for item in competitor_research:
                research_context += f"- {item['title']}: {item['snippet']}\n"
        
        if market_research:
            research_context += "\nBest Practices:\n"
            for item in market_research:
                research_context += f"- {item['title']}\n"
        
        prompt = f"""Write a comprehensive winning RFP proposal for {company}.
        
        PROJECT: {project_name}
        CLIENT: {client_name}
        
        RFP ANALYSIS:
        {analysis}
        
        {research_context}
        
        Create a professional proposal with these sections:
        1. Executive Summary
        2. Understanding of Requirements
        3. Proposed Solution with timeline
        4. Qualifications and Experience
        5. Value Proposition (leverage market research above)
        6. Competitive Advantages (use industry insights)
        7. Why Choose Us
        8. Next Steps
        
        Make it data-driven, persuasive, and professional.
        
        IMPORTANT: Do NOT include any signature block or contact information.
        End with the Next Steps section only."""
        
        response = self.model.generate_content(prompt)
        
        # Add clean signature
        proposal_with_signature = f"""{response.text.strip()}

---

Best regards,

AVIKSOFT LLC
1819 E Southern Ave, Suite D-20
Mesa, AZ 85204
Email: sandeep@aviksoft.com
Phone: (480) 867-5309"""
        
        return proposal_with_signature
    
    def score_proposal(self, proposal_text):
        """Score proposal quality 1-10"""
        scoring_prompt = f"""Analyze this RFP proposal and score it from 1-10 on:
        
        1. Completeness (all required sections)
        2. Specificity (concrete details vs generic claims)
        3. Persuasiveness (compelling value proposition)
        4. Professionalism (structure and tone)
        5. Competitive positioning (differentiation)
        
        Proposal:
        {proposal_text[:5000]}
        
        Provide:
        - Overall Score (1-10)
        - Strengths (2-3 bullet points)
        - Areas to improve (2-3 bullet points)
        
        Format as:
        SCORE: X/10
        STRENGTHS:
        - ...
        IMPROVEMENTS:
        - ..."""
        
        response = self.model.generate_content(scoring_prompt)
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

            body = f"""Dear Client,

Thank you for the opportunity to submit our proposal for {project_name}.

{proposal_text}"""

            msg.attach(MIMEText(body, 'plain'))
        
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, password)
                server.send_message(msg)

        except Exception as e:
            raise Exception(f"Email failed: {str(e)}")

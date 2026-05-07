"""
Multi-Client RFP Processor - Vela AI
Integrates with Gemini API + Gmail
"""

import os
import smtplib
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import google.generativeai as genai
from client_database import ClientDatabase

# Import PDF parsing
try:
    import PyPDF2
except ImportError:
    print("⚠️  PyPDF2 not installed. Run: pip3 install PyPDF2")
    PyPDF2 = None


class RFPProcessor:
    def __init__(self):
        self.db = ClientDatabase()
        self.output_dir = os.path.expanduser("~/rfp-agent/data/client_files")
        
        # Setup Gemini API
        try:
            import streamlit as st
            self.gemini_key = st.secrets.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
            self.gmail_user = st.secrets.get('GMAIL_USER') or os.environ.get('GMAIL_USER')
            self.gmail_password = st.secrets.get('GMAIL_APP_PASSWORD') or os.environ.get('GMAIL_APP_PASSWORD')
        except:
            self.gemini_key = os.environ.get('GEMINI_API_KEY')
            self.gmail_user = os.environ.get('GMAIL_USER')
            self.gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        if not self.gemini_key:
            print("⚠️  GEMINI_API_KEY not set")
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def process_rfp(self, client_id, rfp_file_path, rfp_name):
        """Process RFP for specific client"""
        client = self.db.get_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        print(f"\n{'='*60}")
        print(f"Processing RFP: {rfp_name}")
        print(f"Client: {client['company_name']}")
        print(f"{'='*60}\n")
        
        # Step 1: Extract text from RFP
        print("[1/5] Extracting text from RFP...")
        rfp_text = self.extract_text_from_pdf(rfp_file_path)
        print(f"  ✅ Extracted {len(rfp_text)} characters")
        
        # Step 2: Analyze requirements
        print("[2/5] Analyzing requirements with AI...")
        requirements = self.analyze_requirements(rfp_text, rfp_name)
        print(f"  ✅ Analysis complete")
        
        # Step 3: Load client context
        print("[3/5] Loading client context...")
        client_context = self.build_client_context(client)
        print(f"  ✅ Context loaded")
        
        # Step 4: Generate response
        print("[4/5] Generating proposal response...")
        response = self.generate_response(
            requirements=requirements,
            rfp_text=rfp_text,
            client_context=client_context,
            rfp_name=rfp_name
        )
        print(f"  ✅ Generated {len(response)} characters")
        
        # Step 5: Save and email
        print("[5/5] Saving and notifying client...")
        output_path = self.save_response(client_id, rfp_name, response)
        self.email_client(client, rfp_name, output_path, response)
        
        # Update stats
        self.db.increment_service(client_id, 'rfp')
        
        print(f"\n{'='*60}")
        print("✅ RFP PROCESSING COMPLETE")
        print(f"   Output: {output_path}")
        print(f"   Email sent to: {client['email']}")
        print(f"{'='*60}\n")
        
        return output_path
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        if not PyPDF2:
            return f"[PDF content from {pdf_path}]"
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"  ⚠️  PDF extraction error: {e}")
            return f"[Could not extract PDF. Error: {e}]"
    
    def analyze_requirements(self, rfp_text, rfp_name):
        """Use Gemini AI to analyze RFP requirements"""
        rfp_excerpt = rfp_text[:8000] if len(rfp_text) > 8000 else rfp_text
        
        prompt = f"""
You are analyzing an RFP document to extract key requirements.

RFP: {rfp_name}

Document excerpt:
{rfp_excerpt}

Extract and list:
1. Project scope (what work is being requested)
2. Key requirements (technical, licensing, timeline)
3. Submission deadline
4. Evaluation criteria
5. Budget/value (if mentioned)

Be concise and specific. Format as clear bullet points.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"  ⚠️  AI analysis error: {e}")
            return f"Analysis not available. Error: {e}"
    
    def build_client_context(self, client):
        """Build context about client for personalization"""
        context = f"""
Company: {client['company_name']}
Industry: {client['industry']}
Service Tier: {client['service_tier']}
Past RFPs processed: {client['rfps_processed']}
"""
        
        if client.get('past_wins'):
            context += "\nPast successful projects:\n"
            for win in client['past_wins']:
                context += f"- {win}\n"
        
        return context
    
    def generate_response(self, requirements, rfp_text, client_context, rfp_name):
        """Generate full RFP response using Gemini AI"""
        rfp_excerpt = rfp_text[:6000] if len(rfp_text) > 6000 else rfp_text
        
        prompt = f"""
You are writing a winning RFP response for a construction/consulting company.

{client_context}

RFP Requirements Analysis:
{requirements}

RFP Excerpt:
{rfp_excerpt}

Write a compelling proposal response that includes:

1. EXECUTIVE SUMMARY (2-3 paragraphs)
   - Who we are
   - Why we're the best choice
   - Our unique value proposition

2. PROJECT UNDERSTANDING (3-4 paragraphs)
   - Our interpretation of the requirements
   - Our approach to the work
   - How we'll meet the objectives

3. QUALIFICATIONS & EXPERIENCE
   - Relevant past projects
   - Team expertise
   - Certifications/licenses

4. PROJECT APPROACH & TIMELINE
   - Methodology
   - Key milestones
   - Delivery schedule

5. PRICING (placeholder)
   - Itemized budget categories
   - [Note: Client will fill in actual numbers]

6. REFERENCES
   - List 3 similar projects completed

Write in professional but approachable tone. Be specific, not generic.
Use concrete examples. Address all requirements from the analysis.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=3000,
                )
            )
            
            proposal = response.text.strip()
            
            # Add header
            header = f"""
RFP RESPONSE DRAFT
==================

Project: {rfp_name}
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Powered by Vela AI

NOTE: This is an AI-generated draft. Please review and customize:
- Add specific pricing details
- Update with actual project references
- Verify all technical specifications
- Add company-specific details

==================

"""
            
            return header + proposal
        
        except Exception as e:
            print(f"  ⚠️  Response generation error: {e}")
            return f"Response generation failed. Error: {e}"
    
    def save_response(self, client_id, rfp_name, response):
        """Save generated response to client folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in rfp_name if c.isalnum() or c in (' ', '-', '_'))
        filename = f"{safe_name}_{timestamp}.txt"
        
        client_folder = os.path.join(self.output_dir, client_id, "rfps")
        Path(client_folder).mkdir(parents=True, exist_ok=True)
        
        output_path = os.path.join(client_folder, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response)
        
        return output_path
    
    def email_client(self, client, rfp_name, file_path, response_text):
        """Send email to client with RFP response"""
        if not self.gmail_user or not self.gmail_password:
            print("  ⚠️  Gmail credentials not set. Skipping email.")
            return
        
        msg = MIMEMultipart()
        msg['Subject'] = f"✅ Your RFP Response: {rfp_name}"
        msg['From'] = self.gmail_user
        msg['To'] = client['email']
        
        body = f"""
Hi {client['company_name']} team,

Your RFP response for "{rfp_name}" is ready!

We've analyzed the requirements and generated a customized proposal draft.

NEXT STEPS:
1. Review the attached response
2. Customize pricing and specific details
3. Add your company letterhead
4. Submit before the deadline

The AI has drafted 80% of the work. You just need to review and personalize the final 20%.

Questions? Reply to this email.

Best regards,
Vela AI Team
AVIKSOFT LLC
1819 E Southern Ave, Suite D-20
Mesa, AZ 85204
sandeep@aviksoft.com

---
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Powered by Vela AI - RFP Intelligence Engine
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with open(file_path, 'rb') as f:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(file_path)}'
                )
                msg.attach(attachment)
        except Exception as e:
            print(f"  ⚠️  Could not attach file: {e}")
        
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.sendmail(self.gmail_user, client['email'], msg.as_string())
            
            print(f"  ✅ Email sent to {client['email']}")
        
        except Exception as e:
            print(f"  ⚠️  Email send failed: {e}")


# Test
if __name__ == "__main__":
    processor = RFPProcessor()
    print("✅ Vela AI RFP Processor initialized")
    print(f"   Gemini API: {'✅ Ready' if processor.gemini_key else '❌ Not configured'}")
    print(f"   Gmail SMTP: {'✅ Ready' if processor.gmail_user else '❌ Not configured'}")

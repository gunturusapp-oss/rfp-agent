import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from datetime import datetime
import json

class SheetsTracker:
    def __init__(self):
        """Initialize Google Sheets connection"""
        try:
            # Get credentials from Streamlit secrets
            creds_dict = {
                "type": "service_account",
                "project_id": st.secrets.get("GSHEET_PROJECT_ID", ""),
                "private_key_id": st.secrets.get("GSHEET_PRIVATE_KEY_ID", ""),
                "private_key": st.secrets.get("GSHEET_PRIVATE_KEY", "").replace('\\n', '\n'),
                "client_email": st.secrets.get("GSHEET_CLIENT_EMAIL", ""),
                "client_id": st.secrets.get("GSHEET_CLIENT_ID", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
            
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            self.client = gspread.authorize(creds)
            self.enabled = True
        except Exception as e:
            st.warning(f"⚠️ Google Sheets tracking disabled: {str(e)}")
            self.enabled = False
    
    def log_rfp(self, project_name, client_name, quality_score=None, 
                email_sent=False, proposal_generated=False):
        """Log RFP processing to Google Sheets"""
        if not self.enabled:
            return False
        
        try:
            # Open or create spreadsheet
            sheet_name = st.secrets.get("GSHEET_NAME", "Vela AI - RFP Tracker")
            
            try:
                sheet = self.client.open(sheet_name).sheet1
            except:
                # Create new spreadsheet if doesn't exist
                spreadsheet = self.client.create(sheet_name)
                sheet = spreadsheet.sheet1
                
                # Add headers
                headers = [
                    "Timestamp",
                    "Project Name",
                    "Client Name",
                    "Quality Score",
                    "Proposal Generated",
                    "Email Sent",
                    "Status"
                ]
                sheet.append_row(headers)
            
            # Prepare row data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "✅ Complete" if (proposal_generated and email_sent) else "⏳ In Progress"
            
            row = [
                timestamp,
                project_name,
                client_name,
                quality_score if quality_score else "N/A",
                "Yes" if proposal_generated else "No",
                "Yes" if email_sent else "No",
                status
            ]
            
            # Append row
            sheet.append_row(row)
            return True
            
        except Exception as e:
            st.warning(f"Could not log to Google Sheets: {str(e)}")
            return False
    
    def get_stats(self):
        """Get statistics from tracked RFPs"""
        if not self.enabled:
            return None
        
        try:
            sheet_name = st.secrets.get("GSHEET_NAME", "Vela AI - RFP Tracker")
            sheet = self.client.open(sheet_name).sheet1
            
            # Get all records (skip header)
            records = sheet.get_all_records()
            
            if not records:
                return {
                    "total_rfps": 0,
                    "avg_score": 0,
                    "success_rate": 0,
                    "time_saved_hours": 0
                }
            
            # Calculate stats
            total = len(records)
            
            # Average quality score
            scores = [float(r.get("Quality Score", 0)) for r in records 
                     if r.get("Quality Score") and r.get("Quality Score") != "N/A"]
            avg_score = round(sum(scores) / len(scores), 1) if scores else 0
            
            # Success rate (proposals generated and sent)
            successes = sum(1 for r in records if r.get("Status") == "✅ Complete")
            success_rate = round((successes / total * 100), 0) if total > 0 else 0
            
            # Time saved (assume 12 hours saved per RFP)
            time_saved = total * 12
            
            return {
                "total_rfps": total,
                "avg_score": avg_score,
                "success_rate": success_rate,
                "time_saved_hours": time_saved
            }
            
        except Exception as e:
            st.warning(f"Could not fetch stats: {str(e)}")
            return None

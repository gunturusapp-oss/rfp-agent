import streamlit as st
import re

def analyze_rfp_and_suggest(rfp_text, analysis_text):
    """Analyze RFP and provide smart suggestions"""
    
    suggestions = []
    
    # Check for safety emphasis
    if re.search(r'safety|OSHA|EMR|incident|accident', rfp_text, re.IGNORECASE):
        suggestions.append({
            "icon": "🦺",
            "title": "Safety Focus Detected",
            "suggestion": "This RFP emphasizes safety. Highlight your EMR rating and zero-incident track record."
        })
    
    # Check for timeline/schedule emphasis
    if re.search(r'fast.?track|aggressive|timeline|deadline|expedited', rfp_text, re.IGNORECASE):
        suggestions.append({
            "icon": "⚡",
            "title": "Fast-Track Schedule",
            "suggestion": "Tight timeline detected. Emphasize your phasing strategy and weekend/overtime capabilities."
        })
    
    # Check for sustainability
    if re.search(r'LEED|sustainable|green|energy.?efficient', rfp_text, re.IGNORECASE):
        suggestions.append({
            "icon": "🌱",
            "title": "Sustainability Required",
            "suggestion": "LEED/sustainability mentioned. Highlight your LEED AP credentials and past green building experience."
        })
    
    # Check for budget emphasis
    budget_match = re.search(r'\$[\d,]+(?:M|million|K|thousand)', rfp_text, re.IGNORECASE)
    if budget_match:
        suggestions.append({
            "icon": "💰",
            "title": "Budget Specified",
            "suggestion": f"Budget mentioned: {budget_match.group()}. Consider value engineering proposals to demonstrate cost-consciousness."
        })
    
    # Check for local participation
    if re.search(r'local|DBE|small.?business|disadvantaged', rfp_text, re.IGNORECASE):
        suggestions.append({
            "icon": "🤝",
            "title": "Local Participation Valued",
            "suggestion": "Local/DBE participation encouraged. Emphasize your local subcontractor relationships."
        })
    
    # Check for historic preservation
    if re.search(r'historic|preservation|heritage|mid.?century', rfp_text, re.IGNORECASE):
        suggestions.append({
            "icon": "🏛️",
            "title": "Historic Preservation",
            "suggestion": "Historic elements mentioned. Highlight experience with sensitive renovation and preservation standards."
        })
    
    # Check for occupied space
    if re.search(r'occupied|ongoing.?operations|phased|working.?hours', rfp_text, re.IGNORECASE):
        suggestions.append({
            "icon": "👥",
            "title": "Occupied Facility",
            "suggestion": "Construction during occupancy. Emphasize noise control, dust mitigation, and phased approach."
        })
    
    return suggestions


def display_suggestions(suggestions):
    """Display smart suggestions panel"""
    if not suggestions:
        return
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 15px; border-radius: 10px; margin-bottom: 15px;">
        <h3 style="color: white; margin: 0;">💡 AI-Powered Insights</h3>
        <p style="color: white; margin: 5px 0; opacity: 0.9;">
            Based on this RFP, consider highlighting:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    for suggestion in suggestions:
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 8px; 
                    margin-bottom: 10px; border-left: 4px solid #f5576c;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 8px 0; color: #333;">
                {suggestion['icon']} {suggestion['title']}
            </h4>
            <p style="margin: 0; color: #666; font-size: 0.95em;">
                {suggestion['suggestion']}
            </p>
        </div>
        """, unsafe_allow_html=True)

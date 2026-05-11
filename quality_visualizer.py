import streamlit as st
import re

def display_quality_score(score_text):
    """Display quality score with visual elements"""
    
    try:
        # Parse the score
        score_match = re.search(r'SCORE:\s*(\d+\.?\d*)/10', score_text)
        if not score_match:
            st.markdown(score_text)
            return
        
        overall_score = float(score_match.group(1))
        
        # Create visual score display
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0;">📊 Proposal Quality Analysis</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Overall score with gauge
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Score gauge
            score_percentage = (overall_score / 10) * 100
            stars = "⭐" * int(overall_score)
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: white; 
                        border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="margin: 0; color: #667eea; font-size: 3em;">{overall_score}/10</h1>
                <p style="margin: 10px 0; font-size: 1.5em;">{stars}</p>
                <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea, #764ba2); 
                                width: {score_percentage}%; height: 100%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Parse category scores
        categories = {
            "Technical Completeness": 0,
            "Strategic Insights": 0,
            "Competitive Position": 0,
            "Persuasiveness": 0,
            "Professionalism": 0
        }
        
        # Try to extract individual scores from text
        # This is a simplified version - adjust based on actual format
        for category in categories.keys():
            pattern = f"{category}.*?(\\d+)/10"
            match = re.search(pattern, score_text, re.IGNORECASE)
            if match:
                categories[category] = int(match.group(1))
        
        # Display category breakdown
        st.markdown("### Category Breakdown")
        
        for category, score in categories.items():
            if score > 0:
                # Create progress bar
                col1, col2 = st.columns([3, 1])
                with col1:
                    bar_length = score * 10
                    color = "#4CAF50" if score >= 8 else "#FF9800" if score >= 6 else "#F44336"
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 15px;">
                        <p style="margin: 5px 0; font-weight: 500;">{category}</p>
                        <div style="background: #e0e0e0; height: 25px; border-radius: 5px; overflow: hidden;">
                            <div style="background: {color}; width: {bar_length}%; height: 100%; 
                                        display: flex; align-items: center; padding-left: 10px;">
                                <span style="color: white; font-weight: bold; font-size: 0.9em;">
                                    {'█' * score}
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{score}/10**")
        
        # Parse strengths and improvements
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Strengths")
            strengths_match = re.search(r'STRENGTHS?:(.*?)(?:IMPROVEMENT|$)', score_text, re.DOTALL | re.IGNORECASE)
            if strengths_match:
                strengths = strengths_match.group(1).strip()
                # Parse bullet points
                bullets = re.findall(r'[-•]\s*(.+)', strengths)
                for bullet in bullets[:3]:  # Show top 3
                    st.success(f"✓ {bullet.strip()}")
        
        with col2:
            st.markdown("### ⚠️ Areas to Improve")
            improvements_match = re.search(r'IMPROVEMENT.*?:(.*?)$', score_text, re.DOTALL | re.IGNORECASE)
            if improvements_match:
                improvements = improvements_match.group(1).strip()
                bullets = re.findall(r'[-•]\s*(.+)', improvements)
                for bullet in bullets[:3]:  # Show top 3
                    st.warning(f"→ {bullet.strip()}")
        
    except Exception as e:
        # Fallback to plain text if parsing fails
        st.markdown(score_text)


def display_stats_dashboard(stats):
    """Display statistics dashboard"""
    if not stats:
        return
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0;">📊 Your Performance Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Total RFPs",
            value=stats["total_rfps"],
            delta=None
        )
    
    with col2:
        st.metric(
            label="⭐ Avg Score",
            value=f"{stats['avg_score']}/10",
            delta=None
        )
    
    with col3:
        st.metric(
            label="✅ Success Rate",
            value=f"{stats['success_rate']}%",
            delta=None
        )
    
    with col4:
        st.metric(
            label="⏱️ Time Saved",
            value=f"{stats['time_saved_hours']} hrs",
            delta=None
        )

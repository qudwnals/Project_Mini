import streamlit as st
from ..styles import DashboardStyles

class MetricsComponent:
    def render(self, metrics, selected_region):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(DashboardStyles.render_metric_card(
                f"종합 감성지수 ({selected_region})", 
                f"{metrics['sentiment_avg']:.2f}"
            ), unsafe_allow_html=True)
            
        with col2:
            st.markdown(DashboardStyles.render_metric_card(
                f"경제 변동성 ({selected_region})", 
                f"{metrics['volatility']:.1f}%"
            ), unsafe_allow_html=True)
            
        with col3:
            color = "#2ecc71" if metrics["k_change"] > 0 else "#e74c3c"
            st.markdown(DashboardStyles.render_metric_card(
                "코스피(KOSPI) 변동", 
                f"{metrics['k_change']:+.2f}%",
                color
            ), unsafe_allow_html=True)
            
        with col4:
            color = "#2ecc71" if metrics["q_change"] > 0 else "#e74c3c"
            st.markdown(DashboardStyles.render_metric_card(
                "코스닥(KOSDAQ) 변동", 
                f"{metrics['q_change']:+.2f}%",
                color
            ), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

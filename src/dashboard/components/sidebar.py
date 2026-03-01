import streamlit as st
from datetime import datetime, timedelta

class SidebarComponent:
    def render(self):
        st.sidebar.title("지능형 지역 경제 & 자산 분석")
        st.sidebar.markdown("---")
        
        start_date = st.sidebar.date_input("분석 시작일", datetime.now() - timedelta(days=30))
        end_date = st.sidebar.date_input("분석 종료일", datetime.now())
        asset_type = st.sidebar.radio("자산 종류", ["코스피(KOSPI)", "코스닥(KOSDAQ)"])
        selected_region = st.sidebar.selectbox("분석 지역 선택", ["전국", "서울", "경기도", "강원도", "충청도", "전라도", "경상도"])
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "asset_type": asset_type,
            "selected_region": selected_region
        }

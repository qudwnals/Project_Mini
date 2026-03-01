import streamlit as st
import streamlit.components.v1 as components
from ..styles import DashboardStyles

class MiddleViewComponent:
    def render(self, map_html, issue_df, selected_region):
        mid_col1, mid_col2 = st.columns([1.5, 1])
        
        with mid_col1:
            st.subheader(f"📍 인터랙티브 경제 지도")
            if map_html:
                components.html(map_html, height=600, scrolling=True)
            else:
                st.error("지도 모듈 파일을 불러올 수 없습니다.")

        with mid_col2:
            st.subheader(f"🔥 {selected_region} 핵심 이슈 TOP 10")
            if not issue_df.empty:
                max_count = issue_df['count'].max()
                for _, row in issue_df.iterrows():
                    fill_pct = int((row['count'] / max_count) * 100)
                    st.markdown(DashboardStyles.render_issue_item(
                        row['rank'], row['issue'], row['count'], 
                        row['sentiment'], row['score_display'], fill_pct
                    ), unsafe_allow_html=True)
            else:
                st.info("이슈 데이터가 없습니다.")

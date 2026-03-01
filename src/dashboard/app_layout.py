import streamlit as st
import os
from .data_provider import DataProvider
from .styles import DashboardStyles
from .components.sidebar import SidebarComponent
from .components.metrics import MetricsComponent
from .components.middle_view import MiddleViewComponent
from .components.combo_chart import ComboChartComponent
from .components.detail_tabs import DetailTabsComponent

class DashboardApp:
    def __init__(self, root_path):
        self.root_path = root_path
        self.data_provider = DataProvider(root_path)
        
        # 컴포넌트 초기화
        self.sidebar = SidebarComponent()
        self.metrics_view = MetricsComponent()
        self.middle_view = MiddleViewComponent()
        self.combo_chart = ComboChartComponent()
        self.detail_tabs = DetailTabsComponent(self.data_provider)

    def run(self):
        # 1. 페이지 설정 및 스타일 적용
        st.set_page_config(page_title="지능형 지역 경제 모니터링 대시보드", page_icon="📈", layout="wide")
        st.markdown(DashboardStyles.MAIN_CSS, unsafe_allow_html=True)
        
        # 2. 헤더 렌더링
        st.markdown('<div class="main-title">지능형 지역 경제 모니터링 및 자산 영향 분석 대시보드</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">실시간 뉴스 감성 분석과 자산 영향 분석 통합 대시보드</div>', unsafe_allow_html=True)
        
        # 3. 사이드바 렌더링 및 필터 데이터 획득
        filters = self.sidebar.render()
        
        # 4. 데이터 로딩
        with st.spinner('데이터를 분석 중입니다...'):
            metrics_data = self.data_provider.get_metrics_data(
                filters['start_date'], filters['end_date'], filters['selected_region']
            )
            map_html = self.data_provider.load_official_map(
                filters['start_date'], filters['end_date']
            )
            issue_df = self.data_provider.get_issue_list_data(filters['selected_region'])
            chart_df = self.data_provider.get_chart_data(
                filters['start_date'], filters['end_date'], 
                filters['selected_region'], filters['asset_type']
            )
        
        # 5. UI 섹션 렌더링
        self.metrics_view.render(metrics_data, filters['selected_region'])
        
        self.middle_view.render(map_html, issue_df, filters['selected_region'])
        
        self.combo_chart.render(chart_df, filters['selected_region'], filters['asset_type'])
        
        self.detail_tabs.render(
            chart_df, filters['start_date'], filters['end_date'], 
            filters['selected_region'], filters['asset_type']
        )
        
        # 6. 푸터
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #999;'>© 2026 지능형 지역 경제 & 자산 분석 시스템</p>", unsafe_allow_html=True)

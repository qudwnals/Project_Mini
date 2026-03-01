import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import timedelta
try:
    import FinanceDataReader as fdr
except ImportError:
    fdr = None

class DetailTabsComponent:
    def __init__(self, data_provider):
        self.data_provider = data_provider

    def render(self, chart_df, start_date, end_date, selected_region, asset_type):
        tab1, tab2, tab3, tab4 = st.tabs(["상관관계 분석", "감성 타임라인", "성과 분석", "최신 뉴스"])
        
        with tab1: self._render_correlation_tab(chart_df, start_date, end_date, asset_type)
        with tab2: self._render_timeline_tab(chart_df, selected_region)
        with tab3: self._render_performance_tab(start_date, end_date, asset_type, chart_df)
        with tab4: self._render_news_tab(selected_region)

    def _render_correlation_tab(self, chart_df, start_date, end_date, asset_type):
        st.write(f"### 🔍 감성-자산 상관관계 분석")
        if not chart_df.empty and fdr is not None:
            try:
                k_df = fdr.DataReader('KS11', start_date, end_date)[['Close']].rename(columns={'Close': 'KOSPI'})
                q_df = fdr.DataReader('KQ11', start_date, end_date)[['Close']].rename(columns={'Close': 'KOSDAQ'})
                k_df.index = k_df.index.date.astype(str)
                q_df.index = q_df.index.date.astype(str)
                
                total_corr_df = chart_df[['date', 'sentiment_index']].merge(k_df, left_on='date', right_index=True)
                total_corr_df = total_corr_df.merge(q_df, left_on='date', right_index=True)
                
                corr_input = total_corr_df[['sentiment_index', 'KOSPI', 'KOSDAQ']].rename(columns={'sentiment_index': '감성'})
                matrix = corr_input.corr()
                labels = ['감성', 'KOSPI', 'KOSDAQ']
                
                btm_col1, btm_col2 = st.columns(2)
                with btm_col1:
                    fig_heatmap = px.imshow(matrix, text_auto=".2f", x=labels, y=labels, color_continuous_scale='RdBu_r', range_color=[-1, 1])
                    fig_heatmap.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                with btm_col2:
                    target_col = 'KOSPI' if 'KOSPI' in asset_type else 'KOSDAQ'
                    fig_scatter = px.scatter(total_corr_df, x='sentiment_index', y=target_col, trendline="ols", template="plotly_white")
                    st.plotly_chart(fig_scatter, use_container_width=True)
            except Exception as e:
                st.warning(f"데이터 연동 중 오류 발생: {e}")
        else:
            st.info("데이터가 부족합니다.")

    def _render_timeline_tab(self, chart_df, selected_region):
        st.write(f"### 📅 {selected_region} 일별 감성 캘린더")
        if not chart_df.empty:
            cal_df = chart_df.copy()
            cal_df['date'] = pd.to_datetime(cal_df['date'])
            cal_df['day'] = cal_df['date'].dt.day
            cal_df['week'] = cal_df['date'].dt.isocalendar().week
            cal_df['weekday'] = cal_df['date'].dt.weekday
            
            z_data = cal_df.pivot_table(index='week', columns='weekday', values='sentiment_index').reindex(columns=range(7))
            t_data = cal_df.pivot_table(index='week', columns='weekday', values='day').reindex(columns=range(7))
            
            fig_cal = px.imshow(z_data, x=['월','화','수','목','금','토','일'], y=z_data.index, color_continuous_scale='RdBu_r', range_color=[0, 1])
            fig_cal.update_traces(text=t_data, texttemplate="%{text}", hovertemplate="<b>%{x}요일</b><br>감성: %{z:.2f}<extra></extra>")
            st.plotly_chart(fig_cal, use_container_width=True)
            
            st.markdown("---")
            sorted_dates = sorted(chart_df['date'].unique())
            s_date = st.select_slider("날짜 선택", options=sorted_dates, value=sorted_dates[-1])
            day_news = self.data_provider.get_combined_df("SELECT title, sentiment_score, url, region FROM news WHERE date(published_time) = ?", params=(str(s_date),))
            if selected_region != "전국":
                day_news = day_news[day_news['region'].str.contains(selected_region, na=False)]
            
            c1, c2 = st.columns([1, 2])
            day_avg = chart_df[chart_df['date'] == s_date]['sentiment_index'].values[0]
            with c1:
                st.metric(label=f"{s_date} 종합", value="🚀 긍정" if day_avg > 0.55 else "📉 부정" if day_avg < 0.45 else "☁️ 중립", delta=f"{day_avg:.2f}")
            with c2:
                for _, row in day_news.sort_values('sentiment_score', ascending=False).head(5).iterrows():
                    st.markdown(f"{'🟢' if row['sentiment_score'] > 0.5 else '🔴'} [{row['title']}]({row['url']})")
        else:
            st.warning("데이터가 부족합니다.")

    def _render_performance_tab(self, start_date, end_date, asset_type, chart_df):
        st.write(f"### 💹 {asset_type} 기술적 지표 및 변동성 분석")
        if fdr is not None:
            try:
                # 1. 이동평균선을 구하려면 과거 데이터가 더 필요하므로 시작일을 60일 더 앞으로 당겨서 가져옵니다.
                tech_start = start_date - timedelta(days=60)
                symbol = 'KS11' if "KOSPI" in asset_type or "코스피" in asset_type else 'KQ11'
                df_tech = fdr.DataReader(symbol, tech_start, end_date).reset_index()
                
                if not df_tech.empty:
                    # 2. 기술적 지표 계산 (Pandas 활용)
                    df_tech['MA20'] = df_tech['Close'].rolling(window=20).mean() # 20일 이동평균선
                    df_tech['StdDev'] = df_tech['Close'].rolling(window=20).std() # 20일 표준편차
                    df_tech['Upper_Band'] = df_tech['MA20'] + (df_tech['StdDev'] * 2) # 볼린저 밴드 상단
                    df_tech['Lower_Band'] = df_tech['MA20'] - (df_tech['StdDev'] * 2) # 볼린저 밴드 하단
                    
                    # 3. 화면에 그릴 때는 사용자가 선택한 기간만 잘라서 보여줍니다.
                    df_tech['Date_str'] = df_tech['Date'].dt.date.astype(str)
                    mask = (df_tech['Date'].dt.date >= start_date) & (df_tech['Date'].dt.date <= end_date)
                    df_plot = df_tech.loc[mask]
                    
                    # 4. 차트 그리기
                    fig_tech = go.Figure()
                    
                    # 종가 선
                    fig_tech.add_trace(go.Scatter(x=df_plot['Date_str'], y=df_plot['Close'], name='실제 주가(종가)', line=dict(color='#2c3e50', width=2)))
                    # 20일 이동평균선
                    fig_tech.add_trace(go.Scatter(x=df_plot['Date_str'], y=df_plot['MA20'], name='20일 추세선(MA20)', line=dict(color='#f39c12', width=2)))
                    # 볼린저 밴드 (상단~하단 색칠)
                    fig_tech.add_trace(go.Scatter(x=df_plot['Date_str'], y=df_plot['Upper_Band'], name='변동성 상단', line=dict(color='rgba(52, 152, 219, 0.6)', dash='dash')))
                    fig_tech.add_trace(go.Scatter(x=df_plot['Date_str'], y=df_plot['Lower_Band'], name='변동성 하단', fill='tonexty', fillcolor='rgba(52, 152, 219, 0.15)', line=dict(color='rgba(52, 152, 219, 0.6)', dash='dash')))
                    
                    if not chart_df.empty:
                        fig_tech.add_trace(go.Scatter(
                            x=chart_df['date'], 
                            y=chart_df['sentiment_index'], 
                            name="지역 감성 지수", 
                            line=dict(color='#8e44ad', width=2.5, dash='dot', shape='spline'), # 보라색 점선, 부드러운 곡선 처리
                            yaxis='y2'
                        ))

                    fig_tech.update_layout(
                        height=500, 
                        template="plotly_white", 
                        hovermode="x unified",
                        xaxis=dict(range=[start_date, end_date]), # 사이드바 날짜 고정
                        yaxis=dict(title=f"{asset_type} 가격"), # 왼쪽 Y축 (주가)
                        yaxis2=dict(title="감성 지수", overlaying="y", side="right", range=[0, 1], showgrid=False), # 오른쪽 Y축 (감성)
                        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_tech, use_container_width=True)
                    
                    # 5. 실제 역사적 변동성(Historical Volatility) 계산 (연율화)
                    daily_returns = df_plot['Close'].pct_change().dropna()
                    if not daily_returns.empty:
                        historical_volatility = daily_returns.std() * np.sqrt(252) * 100
                        st.info(f"💡 **분석 포인트:** 현재 선택하신 기간 동안 {asset_type}의 실제 주가 변동성(연환산)은 약 **{historical_volatility:.2f}%** 입니다. 볼린저 밴드(파란 영역)가 넓어질수록 시장의 불안정성(변동폭)이 커짐을 의미합니다.")
            except Exception as e:
                st.error(f"기술적 지표를 계산하는 중 오류가 발생했습니다: {e}")
        else:
            st.warning("FinanceDataReader 라이브러리가 설치되어 있지 않아 분석을 실행할 수 없습니다.")

    def _render_news_tab(self, selected_region):
        st.write(f"#### 📰 {selected_region} 최신 뉴스")
        n_df = self.data_provider.get_combined_df("SELECT title, sentiment_score, published_time as date, url, region FROM news")
        if not n_df.empty:
            if selected_region != "전국": n_df = n_df[n_df['region'].str.contains(selected_region, na=False)]
            for _, row in n_df.sort_values('date', ascending=False).head(5).iterrows():
                color = "#2ecc71" if row["sentiment_score"] > 0.5 else "#e74c3c"
                st.markdown(f'<div style="padding:10px; border-left:5px solid {color}; background-color:#f9f9f9; margin-bottom:10px; border-radius:4px;"><div style="font-size:0.8em; color:#888;">{row["date"]} | 감성: {row["sentiment_score"]:.2f}</div><div style="font-weight:bold;"><a href="{row["url"]}" target="_blank" style="text-decoration:none; color:#333;">{row["title"]}</a></div></div>', unsafe_allow_html=True)

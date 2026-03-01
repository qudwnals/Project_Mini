import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class ComboChartComponent:
    def render(self, chart_df, selected_region, asset_type):
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"📊 {selected_region} 감성 지수 및 자산 가격 추이")
        
        if not chart_df.empty:
            fig = go.Figure()
            real_values = chart_df['sentiment_index']
            display_values = np.where(real_values < 0, np.abs(real_values), real_values)
            colors = np.where(real_values < 0, 'rgba(231, 76, 60, 0.8)', 'rgba(100, 149, 237, 0.6)')

            fig.add_trace(go.Bar(
                x=chart_df['date'],
                y=display_values,
                name=f"{selected_region} 감성 지수",
                marker_color=colors,
                yaxis='y1',
                customdata=real_values,
                hovertemplate="날짜: %{x}<br>실제 감성: %{customdata:.3f}<br>표시값: %{y:.3f}<extra></extra>"
            ))

            if 'asset_price' in chart_df.columns:
                fig.add_trace(go.Scatter(
                    x=chart_df['date'],
                    y=chart_df['asset_price'],
                    name=asset_type,
                    line=dict(color='firebrick', width=3),
                    yaxis='y2'
                ))

            fig.update_layout(
                yaxis=dict(title="감성 지수 (0~1)", range=[0, 1]),
                yaxis2=dict(title=f"{asset_type} 가격", side="right", overlaying="y", showgrid=False),
                height=450,
                template="plotly_white",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"⚠️ {selected_region} 지역의 해당 기간 내 분석 데이터가 존재하지 않습니다.")

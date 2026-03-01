import streamlit as st

class DashboardStyles:
    MAIN_CSS = """
    <style>
        .main-title { background: linear-gradient(90deg, #1f77b4, #2ecc71); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 800; margin-bottom: 1rem; }
        .sub-title { color: #666; font-size: 1.2rem; margin-bottom: 2rem; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; }
        .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #f0f2f6; text-align: center; }
        .metric-label { font-size: 14px; color: #666; margin-bottom: 5px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #1f77b4; }
        .badge-pos { background-color: #d4edda; color: #155724; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .badge-neg { background-color: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    </style>
    """

    @staticmethod
    def render_metric_card(label, value, color="#1f77b4"):
        return f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color: {color};">{value}</div>
        </div>
        """

    @staticmethod
    def render_issue_item(rank, issue, count, sentiment, score, fill_pct):
        badge_class = "badge-pos" if sentiment == "긍정" else "badge-neg"
        badge_icon = "▲ 긍정" if sentiment == "긍정" else "▼ 부정"
        bg_color = "rgba(46, 204, 113, 0.15)" if sentiment == "긍정" else "rgba(231, 76, 60, 0.15)"
        
        return f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 12px; margin-bottom:8px; border-radius:6px; border: 1px solid #f0f2f6; background: linear-gradient(90deg, {bg_color} {fill_pct}%, transparent {fill_pct}%);">
            <span style="font-weight:bold; color:#333;">{rank}. {issue} <span style="font-size:12px; color:#888;">({count}건)</span></span>
            <span class="{badge_class}">{badge_icon} {score}</span>
        </div>
        """

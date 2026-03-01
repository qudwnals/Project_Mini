import pandas as pd
import numpy as np
import sqlite3
import os
import sys
import streamlit as st
from datetime import datetime
try:
    import FinanceDataReader as fdr
except ImportError:
    fdr = None

class DataProvider:
    def __init__(self, root_path):
        self.root_path = root_path
        self.map_module_path = os.path.join(root_path, 'Data_crowling_mini_project', 'map')
        self._setup_map_module()

    def _setup_map_module(self):
        if self.map_module_path not in sys.path:
            sys.path.append(self.map_module_path)
        try:
            from map_generator_geo import NewsMapGeneratorGeo
            self.NewsMapGeneratorGeo = NewsMapGeneratorGeo
            self.MAP_MODULE_AVAILABLE = True
        except ImportError:
            self.MAP_MODULE_AVAILABLE = False

    @st.cache_data(ttl=600)
    def load_official_map(_self, start_date, end_date):
        if not _self.MAP_MODULE_AVAILABLE: return None
        official_path = os.path.join(_self.map_module_path, 'news_map_geo.html')
        
        generator = _self.NewsMapGeneratorGeo()
        generator.generate(start_date, end_date, official_path)
        
        if os.path.exists(official_path):
            with open(official_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def get_combined_df(self, query, params=None):
        df_list = []
        for db_file in ['news.db', 'news_scraped.db']:
            try:
                full_path = os.path.join(self.root_path, 'data', db_file)
                if os.path.exists(full_path):
                    conn = sqlite3.connect(full_path)
                    df = pd.read_sql(query, conn, params=params)
                    conn.close()
                    if not df.empty: df_list.append(df)
            except: continue
        if not df_list: return pd.DataFrame()
        combined_df = pd.concat(df_list, ignore_index=True)
        if 'url' in combined_df.columns:
            combined_df = combined_df.drop_duplicates(subset='url')
        return combined_df

    def get_metrics_data(self, start_date, end_date, region):
        query = "SELECT sentiment_score, url, region FROM news WHERE date(published_time) BETWEEN ? AND ?"
        df = self.get_combined_df(query, params=(start_date.isoformat(), end_date.isoformat()))
        if region != "전국" and not df.empty:
            df = df[df['region'].str.contains(region, na=False)]
        
        avg_s = df['sentiment_score'].mean() if not df.empty and df['sentiment_score'].notnull().any() else 0.5
        cnt = len(df)
        k_change, q_change = 0.0, 0.0
        
        if fdr is not None:
            try:
                k = fdr.DataReader('KS11', start_date, end_date)['Close']
                q = fdr.DataReader('KQ11', start_date, end_date)['Close']
                k_change = ((k.iloc[-1] / k.iloc[0]) - 1) * 100
                q_change = ((q.iloc[-1] / q.iloc[0]) - 1) * 100
            except: pass
        return {'sentiment_avg': avg_s, 'volatility': cnt / 10.0, 'k_change': k_change, 'q_change': q_change}

    def get_issue_list_data(self, region):
        try:
            query = "SELECT keyword, sentiment_score, region FROM news WHERE keyword IS NOT NULL AND keyword != ''"
            df_raw = self.get_combined_df(query)
            if df_raw.empty: return pd.DataFrame()
            if region != "전국":
                df_raw = df_raw[df_raw['region'].str.contains(region, na=False)]
            
            df_raw['sentiment_score'] = df_raw['sentiment_score'].fillna(0.5)
            keyword_stats = {}
            for _, row in df_raw.iterrows():
                tokens = [t.strip() for token in row['keyword'].replace(',', ' ').split() if len(t := token.strip()) >= 2]
                for t in tokens:
                    if t not in keyword_stats: keyword_stats[t] = {'count': 0, 'sent_sum': 0.0}
                    keyword_stats[t]['count'] += 1
                    keyword_stats[t]['sent_sum'] += row['sentiment_score']
            
            if not keyword_stats: return pd.DataFrame()
            res_data = [{'issue': kw, 'count': stat['count'], 'avg_sentiment': stat['sent_sum']/stat['count']} for kw, stat in keyword_stats.items()]
            df = pd.DataFrame(res_data).sort_values('count', ascending=False).head(10)
            df['rank'] = range(1, len(df) + 1)
            df['sentiment'] = np.where(df['avg_sentiment'] >= 0.5, '긍정', '부정')
            df['score_display'] = df['avg_sentiment'].map(lambda x: f"{x:.2f}")
            return df
        except: return pd.DataFrame()

    def get_chart_data(self, start_date, end_date, region, asset_type):
        query = "SELECT date(published_time) as date, sentiment_score, region FROM news WHERE date(published_time) BETWEEN ? AND ?"
        df = self.get_combined_df(query, params=(start_date.isoformat(), end_date.isoformat()))
        if df.empty: return pd.DataFrame()

        region_map = {
            "전라도": ["전남", "전북", "전라"],
            "경상도": ["경남", "경북", "경상"],
            "충청도": ["충남", "충북", "충청"],
            "경기도": ["경기"]
        }

        if region != "전국":
            if region in region_map:
                search_keywords = "|".join(region_map[region])
                df = df[df['region'].str.contains(search_keywords, na=False)]
            else:
                df = df[df['region'].str.contains(region, na=False)]
        
        if df.empty: return pd.DataFrame()

        df_s = df.groupby('date')['sentiment_score'].mean().reset_index()
        df_s.columns = ['date', 'sentiment_index']
        
        if fdr is not None:
            try:
                symbol = 'KQ11' if "코스닥" in asset_type else 'KS11'
                df_p = fdr.DataReader(symbol, start_date, end_date)[['Close']].reset_index()
                df_p.columns = ['date', 'asset_price']
                df_p['date'] = df_p['date'].dt.date.astype(str)
                merged_df = pd.merge(df_s, df_p, on='date', how='left')
                merged_df['asset_price'] = merged_df['asset_price'].ffill().bfill()
                return merged_df
            except: return df_s
        return df_s

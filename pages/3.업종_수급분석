# pages/3_업종별_수급분석.py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="업종별 수급 분석", page_icon="🏭", layout="wide")
BASE_URL = "https://lighthorse.duckdns.org"

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def get_table_list():
    """DB에 있는 모든 테이블 목록을 가져옵니다."""
    try:
        response = requests.get(f"{BASE_URL}/demand/category/tables")
        response.raise_for_status()
        return response.json().get("tables", [])
    except requests.exceptions.RequestException as e:
        st.error(f"테이블 목록 로딩 실패: {e}")
        return []

@st.cache_data(ttl=3600)
def get_table_data(table_name):
    """특정 테이블의 데이터를 가져옵니다."""
    try:
        response = requests.get(f"{BASE_URL}/demand/category/data/{table_name}")
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"'{table_name}' 데이터 로딩 실패: {e}")
        return pd.DataFrame()

# --- UI & LOGIC ---
st.title("🏭 업종별 수급 분석")
st.markdown("업종 및 테마별 기관/외인 수급 스코어 데이터를 조회하고 시계열 변화를 확인합니다.")

table_list = get_table_list()

if table_list:
    selected_table = st.selectbox("분석할 업종/테마를 선택하세요:", options=table_list)
    
    if selected_table:
        data = get_table_data(selected_table)
        
        if not data.empty:
            st.subheader(f"'{selected_table}' 데이터")
            st.dataframe(data, use_container_width=True, height=300)
            
            # 시계열 차트 생성
            if 'Date' in data.columns and 'total_score' in data.columns:
                st.markdown("---")
                st.subheader("📈 수급 스코어 시계열 차트")
                fig = px.line(data, x='Date', y='total_score',
                              title=f"'{selected_table}' 수급 스코어 추이",
                              labels={'total_score': '종합 수급 스코어', 'Date': '날짜'},
                              markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("차트를 그리기 위한 'Date' 또는 'total_score' 컬럼이 없습니다.")
else:
    st.warning("데이터베이스에서 조회할 테이블이 없습니다.")

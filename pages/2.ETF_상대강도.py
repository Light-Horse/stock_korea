# pages/1_ETF_상대강도(RS).py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="ETF 상대강도(RS) 분석", page_icon="📑", layout="wide")
BASE_URL = "https://lighthorse.duckdns.org"

# --- HELPER FUNCTION ---
@st.cache_data(ttl=3600)  # 1시간 동안 캐시
def fetch_data(api_path):
    """API로부터 데이터를 가져와 DataFrame으로 변환합니다."""
    try:
        response = requests.get(f"{BASE_URL}{api_path}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# --- UI & LOGIC ---
st.title("📑 ETF 상대강도(RS) 분석")
st.markdown("ETF의 맨스필드 상대강도(RS)와 다양한 이동평균선 기반 모멘텀 스코어를 조회합니다.")

analysis_type = st.selectbox(
    "조회할 데이터 종류를 선택하세요:",
    ("맨스필드 RS", "모멘텀 스코어")
)

data = pd.DataFrame()

if analysis_type == "맨스필드 RS":
    st.subheader("맨스필드 상대강도 (Mansfield RS)")
    data = fetch_data("/rs-etf/mansfield")
else:
    st.subheader("변동성 조정 모멘텀 스코어")
    momentum_option = st.radio(
        "모멘텀 필터 선택:",
        ["전체", "10일선 필터", "20일선 필터", "50일선 필터"],
        horizontal=True
    )
    api_map = {
        "전체": "/rs-etf/momentum/all",
        "10일선 필터": "/rs-etf/momentum/ma10",
        "20일선 필터": "/rs-etf/momentum/ma20",
        "50일선 필터": "/rs-etf/momentum/ma50"
    }
    data = fetch_data(api_map[momentum_option])

# --- DISPLAY DATA ---
if not data.empty:
    st.dataframe(data, use_container_width=True, height=500)

    # 모멘텀 스코어 차트 시각화
    if analysis_type == "모멘텀 스코어" and 'Date' in data.columns:
        st.markdown("---")
        st.subheader("📈 모멘텀 스코어 시계열 차트")
        
        # 'Date'를 datetime 형식으로 변환
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Melt DataFrame for Plotly
        value_vars = [col for col in data.columns if col != 'Date']
        if value_vars:
            df_melted = data.melt(id_vars='Date', value_vars=value_vars, var_name='ETF', value_name='Score')
            
            fig = px.line(df_melted, x='Date', y='Score', color='ETF',
                          title=f"ETF 모멘텀 스코어 추이 ({momentum_option})",
                          labels={'Score': '모멘텀 스코어', 'Date': '날짜'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("차트를 그릴 데이터가 부족합니다.")

else:
    st.info("선택한 조건에 해당하는 데이터가 없습니다.")

# pages/2_개별주식_상대강도(RS).py
import streamlit as st
import pandas as pd
import requests

# --- CONFIG ---
st.set_page_config(page_title="개별 주식 상대강도(RS) 분석", page_icon="📊", layout="wide")
BASE_URL = "https://lighthorse.duckdns.org"

# --- HELPER FUNCTION ---
@st.cache_data(ttl=3600)
def fetch_stock_data(api_path):
    """API로부터 데이터를 가져옵니다."""
    try:
        response = requests.get(f"{BASE_URL}{api_path}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"데이터 로딩 실패: {e}")
        return pd.DataFrame()

# --- UI & LOGIC ---
st.title("📊 개별 주식 상대강도(RS) 분석")
st.markdown("개별 주식의 맨스필드 상대강도 및 모멘텀 스코어 데이터를 조회하고 검색할 수 있습니다.")

analysis_type = st.selectbox(
    "조회할 데이터 종류를 선택하세요:",
    ("맨스필드 RS", "모멘텀 스코어")
)

api_map = {
    "맨스필드 RS": "/rs-stock/mansfield",
    "모멘텀 스코어": "/rs-stock/momentum"
}
data = fetch_stock_data(api_map[analysis_type])

# --- DISPLAY DATA ---
if not data.empty:
    st.subheader(f"데이터 조회: {analysis_type}")

    # 종목명으로 검색 기능 (모멘텀 스코어에만 적용)
    if analysis_type == "모멘텀 스코어":
        search_term = st.text_input("종목명으로 검색:", placeholder="예: 삼성전자")
        if search_term:
            # '종목명' 컬럼이 존재한다고 가정
            if '종목명' in data.columns:
                filtered_data = data[data['종목명'].str.contains(search_term, na=False)]
                st.dataframe(filtered_data, use_container_width=True, height=500)
            else:
                st.warning("'종목명' 컬럼이 데이터에 없습니다. 검색이 불가능합니다.")
                st.dataframe(data, use_container_width=True, height=500)
        else:
            st.dataframe(data, use_container_width=True, height=500)
    else:
        st.dataframe(data, use_container_width=True, height=500)
else:
    st.info("데이터가 없습니다.")

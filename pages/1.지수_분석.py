import streamlit as st
import requests

# --- CONFIG ---
st.set_page_config(page_title="최신 분석 차트", page_icon="🖼️", layout="wide")
BASE_URL = "https://lighthorse.duckdns.org"

# --- UI & LOGIC ---
st.title("🖼️ 최신 분석 차트")
st.markdown("매일 업데이트되는 FG 및 OS 분석 차트입니다.")

tab1, tab2 = st.tabs(["FG 차트", "OS 차트"])

with tab1:
    st.header("FG 분석 차트")
    st.markdown("가장 최근에 생성된 FG 분석 차트입니다.")
    col1, col2 = st.columns(2)
    with col1:
        # use_column_width -> use_container_width 로 수정
        st.image(f"{BASE_URL}/charts/fg/1", caption="FG 차트 1", use_container_width=True)
    with col2:
        # use_column_width -> use_container_width 로 수정
        st.image(f"{BASE_URL}/charts/fg/2", caption="FG 차트 2", use_container_width=True)

with tab2:
    st.header("OS 분석 차트")
    st.markdown("가장 최근에 생성된 OS 분석 차트입니다.")
    col1, col2 = st.columns(2)
    with col1:
        # use_column_width -> use_container_width 로 수정
        st.image(f"{BASE_URL}/charts/os/1", caption="OS 차트 1", use_container_width=True)
    with col2:
        # use_column_width -> use_container_width 로 수정
        st.image(f"{BASE_URL}/charts/os/2", caption="OS 차트 2", use_container_width=True)

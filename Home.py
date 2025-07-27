import streamlit as st

st.set_page_config(
    page_title="Lighthorse 데이터 분석 대시보드",
    page_icon="🐴",
    layout="wide",
)

st.title("🐴 Lighthorse API 데이터 분석 대시보드")
st.write("---")

st.header("소개")
st.markdown("""
이 웹사이트는 `lighthorse.duckdns.org` API 서버에서 제공하는 다양한 금융 데이터를 시각화하고 분석하기 위해 구축되었습니다.

👈 **왼쪽 사이드바에서 분석하고 싶은 메뉴를 선택하세요.**

각 페이지는 특정 데이터베이스(DB) 또는 분석 주제에 맞춰 구성되어 있습니다.
""")

st.info("""
- **개별 주식 수급 분석**: 특정 종목의 시가총액과 MACD 오실레이터 데이터를 비교 분석합니다.
- **다른 분석 페이지 (예시)**: 향후 다른 종류의 데이터를 분석하는 페이지를 추가할 수 있는 예시입니다.
""", icon="ℹ️")

st.sidebar.success("분석 메뉴를 선택하세요.")

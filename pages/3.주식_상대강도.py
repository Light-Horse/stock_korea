# pages/2_개별주식_상대강도(RS).py
import streamlit as st
import pandas as pd
import requests
from functools import partial

# --- CONFIG ---
st.set_page_config(page_title="개별 주식 상대강도(RS) 분석", page_icon="📊", layout="wide")
BASE_URL = "https://lighthorse.duckdns.org"

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def fetch_stock_data(api_path):
    """API로부터 데이터를 가져옵니다."""
    try:
        response = requests.get(f"{BASE_URL}{api_path}")
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values(by='Date', ascending=False).reset_index(drop=True)
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"데이터 로딩 실패: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return pd.DataFrame()

def style_wide_format(df, highlight_stock=None):
    """
    와이드 포맷 데이터프레임에 순위 변화 및 선택 종목 하이라이트 스타일을 적용합니다.
    """
    # 1. 순위 변화에 따른 배경색 스타일링
    rank_change_styler = pd.DataFrame('', index=df.index, columns=df.columns)
    if 'Date' in df.columns and len(df) >= 2:
        stock_to_rank_map = {}
        for idx, row in df.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            stock_to_rank_map[date_str] = {}
            for col in df.columns:
                if col.startswith('Top'):
                    rank = int(col.split(' ')[1])
                    stock_name = row[col]
                    if pd.notna(stock_name):
                        stock_to_rank_map[date_str][stock_name] = rank
        
        for idx in range(len(df) - 1):
            current_row = df.iloc[idx]
            previous_row = df.iloc[idx + 1]
            previous_ranks = stock_to_rank_map.get(previous_row['Date'].strftime('%Y-%m-%d'), {})
            for col in df.columns:
                if not col.startswith('Top'): continue
                current_rank = int(col.split(' ')[1])
                current_stock = current_row[col]
                if pd.isna(current_stock): continue
                
                previous_rank = previous_ranks.get(current_stock)
                color = ''
                if previous_rank is None:
                    color = 'background-color: rgba(40, 167, 69, 0.4)' # Green
                else:
                    change = previous_rank - current_rank
                    if change > 0:
                        alpha = min(0.3 + (change / 10) * 0.5, 0.8)
                        color = f'background-color: rgba(220, 53, 69, {alpha})' # Red
                    elif change < 0:
                        alpha = min(0.3 + (abs(change) / 10) * 0.5, 0.8)
                        color = f'background-color: rgba(0, 123, 255, {alpha})' # Blue
                if color:
                    rank_change_styler.at[idx, col] = color

    # 2. 선택된 종목에 대한 테두리 스타일링
    if highlight_stock:
        border_style = 'border: 2.5px solid #FF6347 !important;'
        # 배경색 스타일과 테두리 스타일을 결합
        return rank_change_styler.apply(lambda s: s.where(df != highlight_stock, s + border_style))
    
    return rank_change_styler

# --- UI & LOGIC ---
st.title("📊 개별 주식 상대강도(RS) 분석")
st.markdown("개별 주식의 맨스필드 상대강도 및 모멘텀 스코어 데이터를 조회합니다.")

analysis_type = st.selectbox(
    "조회할 데이터 종류를 선택하세요:",
    ("모멘텀 스코어", "맨스필드 RS")
)

api_map = {
    "맨스필드 RS": "/rs-stock/mansfield",
    "모멘텀 스코어": "/rs-stock/momentum"
}
data_raw = fetch_stock_data(api_map[analysis_type])

# --- DISPLAY DATA ---
if not data_raw.empty:
    st.subheader(f"데이터 조회: {analysis_type}")

    if analysis_type == "모멘텀 스코어" and 'Date' in data_raw.columns:
        
        # 💡 1. 강조할 종목을 선택하는 위젯 추가
        stock_columns = [col for col in data_raw.columns if col.startswith('Top')]
        unique_stocks = pd.unique(data_raw[stock_columns].values.ravel('K'))
        unique_stocks = sorted([stock for stock in unique_stocks if pd.notna(stock)])
        
        selected_stock = st.selectbox(
            "강조할 종목 선택 (선택 해제는 '전체 보기' 클릭)",
            options=['전체 보기'] + unique_stocks,
            index=0
        )
        
        highlight_target = selected_stock if selected_stock != '전체 보기' else None

        # 💡 2. 스타일 함수에 선택된 종목 정보 전달
        styled_df = (
            data_raw.style.apply(style_wide_format, highlight_stock=highlight_target, axis=None)
            .format({'Date': lambda x: x.strftime('%m-%d')})
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            height=500,
            hide_index=True
        )
    else:
        st.dataframe(data_raw, use_container_width=True, height=500, hide_index=True)
else:
    st.info("데이터가 없습니다.")

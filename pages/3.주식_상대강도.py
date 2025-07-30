# pages/2_개별주식_상대강도(RS).py
import streamlit as st
import pandas as pd
import requests

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
        
        # '모멘텀 스코어' 데이터일 경우, 날짜를 기준으로 정렬
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

def style_wide_format_by_rank_change(df):
    """
    와이드 포맷 데이터프레임의 순위 변화에 따라 스타일을 적용합니다.
    """
    if 'Date' not in df.columns or len(df) < 2:
        return pd.DataFrame('', index=df.index, columns=df.columns)

    # 1. (날짜, 종목명) -> 순위 조회를 위한 맵 생성
    stock_to_rank_map = {}
    for idx, row in df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        stock_to_rank_map[date_str] = {}
        for col in df.columns:
            if col.startswith('Top'):
                try:
                    rank = int(col.split(' ')[1])
                    stock_name = row[col]
                    if pd.notna(stock_name):
                        stock_to_rank_map[date_str][stock_name] = rank
                except (ValueError, IndexError):
                    continue

    # 2. 스타일을 적용할 비어있는 데이터프레임 생성
    styler_df = pd.DataFrame('', index=df.index, columns=df.columns)
    
    # 3. 최신 날짜부터 역으로 순회하며 전날과 비교
    for idx in range(len(df) - 1):
        current_row = df.iloc[idx]
        previous_row = df.iloc[idx + 1]
        
        previous_date_str = previous_row['Date'].strftime('%Y-%m-%d')
        previous_ranks = stock_to_rank_map.get(previous_date_str, {})

        for col in df.columns:
            if not col.startswith('Top'):
                continue

            current_rank = int(col.split(' ')[1])
            current_stock = current_row[col]

            if pd.isna(current_stock):
                continue

            previous_rank = previous_ranks.get(current_stock)
            
            color = ''
            if previous_rank is None: # 신규 진입
                color = 'rgba(40, 167, 69, 0.4)' # Green
            else:
                change = previous_rank - current_rank
                if change > 0: # 순위 상승
                    alpha = min(0.3 + (change / 10) * 0.5, 0.8)
                    color = f'rgba(220, 53, 69, {alpha})' # Red
                elif change < 0: # 순위 하락
                    alpha = min(0.3 + (abs(change) / 10) * 0.5, 0.8)
                    color = f'rgba(0, 123, 255, {alpha})' # Blue
            
            if color:
                styler_df.at[idx, col] = f'background-color: {color}'
    
    return styler_df

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
        # 화면 표시용 데이터 복사 및 날짜 형식 변경
        display_data = data_raw.copy()
        display_data['Date'] = display_data['Date'].dt.strftime('%m-%d')

        # 데이터프레임에 스타일 적용하여 표시
        st.dataframe(
            display_data.style.apply(style_wide_format_by_rank_change, axis=None),
            use_container_width

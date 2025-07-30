# pages/2_개별주식_상대강도(RS).py
import streamlit as st
import pandas as pd
import requests
import numpy as np

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
        data = pd.DataFrame(response.json())
        # 날짜 형식 변환 및 object 타입으로 변경
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date']).dt.strftime('%m-%d')
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"데이터 로딩 실패: {e}")
        return pd.DataFrame()

def get_rank_change(df):
    """주간 순위 변화를 계산하고 'rank_change' 컬럼을 추가합니다."""
    if 'date' not in df.columns or '종목명' not in df.columns:
        return df

    df_sorted = df.sort_values(by=['date', '순위'], ascending=[False, True])
    dates = sorted(df_sorted['date'].unique(), reverse=True)

    if len(dates) < 2:
        df['rank_change'] = '신규'
        return df

    latest_date = dates[0]
    previous_date = dates[1]

    latest_df = df_sorted[df_sorted['date'] == latest_date].set_index('종목명')
    previous_df = df_sorted[df_sorted['date'] == previous_date].set_index('종목명')

    latest_df['previous_rank'] = previous_df['순위']
    latest_df['rank_change_value'] = latest_df['previous_rank'] - latest_df['순위']
    
    def get_change_label(change):
        if pd.isna(change):
            return '신규'
        elif change > 0:
            return f'▲{int(change)}'
        elif change < 0:
            return f'▼{abs(int(change))}'
        else:
            return '-'

    latest_df['rank_change'] = latest_df['rank_change_value'].apply(get_change_label)
    
    # 원본 데이터프레임에 순위 변화 정보 병합
    df = df.merge(latest_df[['rank_change', 'rank_change_value']], on='종목명', how='left')
    return df


def style_rank_change(row):
    """순위 변화에 따라 행 배경색을 스타일링합니다."""
    style = [''] * len(row)
    change_value = row.get('rank_change_value')

    if pd.isna(change_value): # 신규 진입
        color = 'rgba(40, 167, 69, 0.3)' # Green
    elif change_value > 0: # 순위 상승
        # 상승폭에 따라 진하기 조절 (최대 10 이상일 때 가장 진하게)
        alpha = min(0.2 + (change_value / 10) * 0.5, 0.7)
        color = f'rgba(220, 53, 69, {alpha})' # Red
    elif change_value < 0: # 순위 하락
        # 하락폭에 따라 진하기 조절 (최대 10 이상일 때 가장 진하게)
        alpha = min(0.2 + (abs(change_value) / 10) * 0.5, 0.7)
        color = f'rgba(0, 123, 255, {alpha})' # Blue
    else: # 순위 유지
        color = ''

    if color:
        style = [f'background-color: {color}'] * len(row)
        
    return style

# --- UI & LOGIC ---
st.title("📊 개별 주식 상대강도(RS) 분석")
st.markdown("개별 주식의 맨스필드 상대강도 및 모멘텀 스코어 데이터를 조회하고 시각적으로 순위 변화를 추적합니다.")

analysis_type = st.selectbox(
    "조회할 데이터 종류를 선택하세요:",
    ("모멘텀 스코어", "맨스필드 RS")
)

api_map = {
    "맨스필드 RS": "/rs-stock/mansfield",
    "모멘텀 스코어": "/rs-stock/momentum"
}
data = fetch_stock_data(api_map[analysis_type])

# --- DISPLAY DATA ---
if not data.empty:
    st.subheader(f"데이터 조회: {analysis_type} (Top 20)")

    # 모멘텀 스코어에만 순위 변화 적용
    if analysis_type == "모멘텀 스코어":
        # 순위 계산 및 변화 추적
        data['순위'] = data.groupby('date').cumcount() + 1
        data_with_change = get_rank_change(data)
        
        # 최신 날짜의 Top 20 데이터만 필터링
        latest_date = data_with_change['date'].max()
        top20_data = data_with_change[data_with_change['date'] == latest_date].head(20)

        # 불필요한 컬럼 숨기기
        display_cols = ['순위', 'rank_change', 'date', '종목명', '종목코드', '현재가', '등락률', '시가총액', '모멘텀스코어']
        
        # 'rank_change_value'가 있는 경우에만 스타일 적용
        if 'rank_change_value' in top20_data.columns:
            # 순서 변경 및 rank_change_value 컬럼 제거
            top20_display = top20_data[display_cols].rename(columns={'rank_change': '순위변동'})
            
            st.dataframe(
                top20_display.style.apply(style_rank_change, axis=1),
                use_container_width=True,
                height=735,
                hide_index=True
            )
        else:
            st.dataframe(top20_data, use_container_width=True, height=735, hide_index=True)

    else: # 맨스필드 RS 또는 검색 결과는 기본 테이블로 표시
         st.dataframe(data, use_container_width=True, height=500, hide_index=True)

    # 전체 데이터 검색 기능
    with st.expander("전체 데이터 검색"):
        search_term = st.text_input("종목명으로 검색:", placeholder="예: 삼성전자")
        if search_term:
            if '종목명' in data.columns:
                filtered_data = data[data['종목명'].str.contains(search_term, na=False)]
                st.dataframe(filtered_data, use_container_width=True, height=500, hide_index=True)
            else:
                st.warning("'종목명' 컬럼이 데이터에 없습니다.")
        else:
            st.info("검색창에 종목명을 입력하여 전체 데이터에서 찾아볼 수 있습니다.")

else:
    st.info("데이터가 없습니다.")

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
    """
    API로부터 데이터를 가져오고, '와이드' 포맷을 '롱' 포맷으로 변환합니다.
    """
    try:
        response = requests.get(f"{BASE_URL}{api_path}")
        response.raise_for_status()
        
        # '맨스필드 RS'는 그대로 반환, '모멘텀 스코어'만 변환
        if api_path == "/rs-stock/mansfield":
            return pd.DataFrame(response.json())
        
        # '모멘텀 스코어' 데이터 변환 로직
        wide_data = response.json()
        df_wide = pd.DataFrame(wide_data)
        
        # 'Date' 키가 없는 경우 처리
        if 'Date' not in df_wide.columns:
            st.error("API 응답에 'Date' 키가 없습니다. 데이터 형식을 확인해주세요.")
            return pd.DataFrame()
            
        df_wide = df_wide.set_index('Date')
        
        df_long = df_wide.reset_index().melt(
            id_vars='Date', 
            var_name='순위_임시', 
            value_name='종목명'
        )
        
        df_long['순위'] = df_long['순위_임시'].str.extract('(\d+)').astype(int)
        
        # 'date' 컬럼 이름을 소문자로 통일하고 형식 변경
        df_long = df_long.rename(columns={'Date': 'date'})
        df_long['date'] = pd.to_datetime(df_long['date']).dt.strftime('%m-%d')
        
        final_df = df_long[['date', '순위', '종목명']].sort_values(by=['date', '순위'])
        
        return final_df

    except requests.exceptions.RequestException as e:
        st.error(f"데이터 로딩 실패: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return pd.DataFrame()


def get_rank_change(df):
    """순위 변화를 계산하고 'rank_change' 관련 컬럼을 추가합니다."""
    df_sorted = df.sort_values(by=['date', '순위'], ascending=[False, True])
    dates = sorted(df_sorted['date'].unique(), reverse=True)

    if len(dates) < 2:
        df['rank_change'] = '신규'
        df['rank_change_value'] = float('NaN')
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
    
    # 원본에 병합하기 위해 인덱스 리셋
    df = df.merge(latest_df[['rank_change', 'rank_change_value']].reset_index(), on='종목명', how='left')
    return df


def style_rank_change(row):
    """순위 변화에 따라 행 배경색을 스타일링합니다."""
    style = [''] * len(row)
    change_value = row.get('rank_change_value')

    if pd.isna(change_value):
        color = 'rgba(40, 167, 69, 0.3)' # Green (신규)
    elif change_value > 0: # 순위 상승
        alpha = min(0.2 + (change_value / 10) * 0.5, 0.7)
        color = f'rgba(220, 53, 69, {alpha})' # Red
    elif change_value < 0: # 순위 하락
        alpha = min(0.2 + (abs(change_value) / 10) * 0.5, 0.7)
        color = f'rgba(0, 123, 255, {alpha})' # Blue
    else: # 순위 유지
        color = ''

    if color:
        style = [f'background-color: {color}'] * len(row)
        
    return style

# --- UI & LOGIC ---
st.title("📊 개별 주식 상대강도(RS) 분석")
st.markdown("개별 주식의 맨스필드 상대강도 및 모멘텀 스코어 데이터를 조회하고 검색할 수 있습니다.")

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
    st.subheader(f"데이터 조회: {analysis_type}")

    if analysis_type == "모멘텀 스코어":
        st.markdown("#### 📈 Top 20 순위 변화")
        
        data_with_change = get_rank_change(data)
        
        latest_date = data_with_change['date'].max()
        top20_data = data_with_change[data_with_change['date'] == latest_date].head(20)
        
        display_cols = ['순위', 'rank_change', '종목명', 'date']
        top20_display = top20_data[display_cols].rename(columns={'rank_change': '순위변동'})
        
        st.dataframe(
            top20_display.style.apply(style_rank_change, axis=1),
            use_container_width=True,
            height=735,
            hide_index=True
        )
        
        with st.expander("🔍 전체 데이터 보기 및 검색"):
            search_term_momentum = st.text_input("종목명으로 검색 ", placeholder="예: 삼성전자", key="momentum_search")
            
            if search_term_momentum:
                filtered_data = data_with_change[data_with_change['종목명'].str.contains(search_term_momentum, na=False)]
                st.dataframe(filtered_data, use_container_width=True, height=500, hide_index=True)
            else:
                st.dataframe(data_with_change, use_container_width=True, height=500, hide_index=True)

    else: # 맨스필드 RS
        search_term_mansfield = st.text_input("종목명으로 검색", placeholder="예: 삼성전자", key="mansfield_search")
        if search_term_mansfield:
            if '종목명' in data.columns:
                filtered_data = data[data['종목명'].str.contains(search_term_mansfield, na=False)]
                st.dataframe(filtered_data, use_container_width=True, height=500, hide_index=True)
            else:
                st.warning("'종목명' 컬럼이 데이터에 없습니다. 검색이 불가능합니다.")
        else:
            st.dataframe(data, use_container_width=True, height=500, hide_index=True)
else:
    st.info("데이터가 없습니다.")

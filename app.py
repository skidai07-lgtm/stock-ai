import streamlit as st
import os
from dotenv import load_dotenv
from pykrx import stock
from kis_api import KisApi
from analyzer import StockAnalyzer

# Load environment variables
load_dotenv()

st.set_page_config(page_title="한국 주식 AI 분석기", page_icon="📈", layout="centered")

st.title("📈 한국 주식 AI 종합 분석기")
st.markdown("한국투자증권 실시간 재무 데이터와 Google Gemini AI를 활용하여 종목을 입체적으로 분석합니다.")

# Sidebar for API Keys
with st.sidebar:
    st.header("🔑 API 키 설정")
    st.markdown("`.env` 파일에 키가 설정되어 있으면 자동으로 불러옵니다.")
    kis_app_key = st.text_input("KIS App Key (한투)", value=os.getenv("KIS_APP_KEY", ""), type="password")
    kis_app_secret = st.text_input("KIS App Secret (한투)", value=os.getenv("KIS_APP_SECRET", ""), type="password")
    gemini_api_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    
    st.markdown("---")
    st.markdown("""
    **스마트폰 접속 방법:**
    PC에서 이 프로그램을 실행한 상태로, 스마트폰 브라우저 주소창에
    PC의 로컬 IP 주소와 포트(기본 8501)를 입력하면 스마트폰에서 접속할 수 있습니다.
    예: `http://192.168.0.x:8501`
    """)

# Cache ticker mapping to avoid pykrx slow lookup every time
@st.cache_data(ttl=3600*24)
def get_all_tickers():
    mapping = {}
    with st.spinner("최초 1회 주식 종목 코드를 불러오는 중입니다 (약 10초 소요)..."):
        for market in ["KOSPI", "KOSDAQ"]:
            tickers = stock.get_market_ticker_list(market=market)
            for ticker in tickers:
                name = stock.get_market_ticker_name(ticker)
                mapping[name] = ticker
    return mapping

ticker_dict = get_all_tickers()

st.markdown("---")
stock_name = st.text_input("🔎 분석할 종목명을 입력하세요 (예: 삼성전자, 카카오)")

if st.button("AI 분석 시작하기", use_container_width=True, type="primary"):
    if not kis_app_key or not kis_app_secret or not gemini_api_key:
        st.error("좌측 사이드바에서 모든 API 키를 먼저 입력해주세요.")
    elif not stock_name:
        st.warning("종목명을 입력해주세요.")
    else:
        ticker = ticker_dict.get(stock_name)
        if not ticker:
            st.error(f"'{stock_name}' 종목을 찾을 수 없습니다. 정확한 이름을 입력했는지 확인해주세요.")
            st.stop()
            
        st.success(f"종목 확인 완료: **{stock_name}** ({ticker})")
        
        with st.spinner("한투 API 연동 및 재무 데이터 로딩 중..."):
            try:
                kis = KisApi(kis_app_key, kis_app_secret)
                stock_data = kis.get_stock_data(ticker)
                
                # Display metrics nicely in cards
                st.subheader("📊 핵심 재무 지표")
                cols = st.columns(4)
                cols[0].metric("현재가", f"{int(stock_data.get('현재가', 0)):,} 원")
                cols[1].metric("PER", stock_data.get('PER', 'N/A'))
                cols[2].metric("PBR", stock_data.get('PBR', 'N/A'))
                cols[3].metric("EPS", f"{int(float(stock_data.get('EPS', 0))):,} 원")
                
            except Exception as e:
                st.error(f"한투 API 연동 실패: {e}")
                st.stop()
                
        with st.spinner("AI(Gemini)가 업황과 해외매출 가능성 등을 분석 중입니다... (10~20초 소요)"):
            try:
                analyzer = StockAnalyzer(gemini_api_key)
                report = analyzer.analyze(stock_name, stock_data)
                
                st.markdown("---")
                st.subheader("💡 AI 종합 분석 결과")
                
                # Display markdown report inside a container with some styling
                with st.container(border=True):
                    st.markdown(report)
                    
            except Exception as e:
                st.error(f"AI 분석 실패: {e}")

import streamlit as st
import os
from dotenv import load_dotenv
import FinanceDataReader as fdr
from naver_api import NaverFinanceApi
from analyzer import StockAnalyzer

# Load environment variables
load_dotenv()

st.set_page_config(page_title="한국 주식 AI 분석기", page_icon="📈", layout="centered")

st.title("📈 한국 주식 AI 종합 분석기")
st.markdown("네이버 증권 실시간 재무 데이터와 Google Gemini AI를 활용하여 종목을 입체적으로 분석합니다.")

# Sidebar for API Keys
with st.sidebar:
    st.header("🔑 API 키 설정")
    st.markdown("`.env` 파일에 키가 설정되어 있으면 자동으로 불러옵니다.")
    gemini_api_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    
    st.markdown("---")
    st.markdown("""
    ✅ **장점:** 한투 API를 사용하지 않으므로 기존 자동매매 프로그램과 충돌이 없으며, 로그인 없이 완전 무료로 동작합니다!
    """)
    st.markdown("---")
    st.markdown("""
    **스마트폰 접속 방법:**
    PC에서 이 프로그램을 실행한 상태로, 스마트폰 브라우저 주소창에
    PC의 로컬 IP 주소와 포트(기본 8501)를 입력하면 스마트폰에서 접속할 수 있습니다.
    예: `http://192.168.0.x:8501`
    """)

# Cache ticker mapping to avoid slow lookup every time
@st.cache_data(ttl=3600*24)
def get_all_tickers():
    mapping = {}
    with st.spinner("최초 1회 주식 종목 코드를 불러오는 중입니다 (약 5초 소요)..."):
        df_krx = fdr.StockListing('KRX')
        for idx, row in df_krx.iterrows():
            mapping[row['Name']] = row['Code']
    return mapping

ticker_dict = get_all_tickers()

st.markdown("---")
stock_name = st.text_input("🔎 분석할 종목명을 입력하세요 (예: 삼성전자, 카카오)")

if st.button("AI 분석 시작하기", use_container_width=True, type="primary"):
    if not gemini_api_key:
        st.error("좌측 사이드바에서 Gemini API 키를 먼저 입력해주세요.")
    elif not stock_name:
        st.warning("종목명을 입력해주세요.")
    else:
        user_input = stock_name.strip()
        ticker = None
        
        # 1. 6자리 종목코드를 직접 입력한 경우
        if user_input.isdigit() and len(user_input) == 6:
            ticker = user_input
            # 원래 이름 찾기 (출력용)
            for name, code in ticker_dict.items():
                if code == ticker:
                    stock_name = name
                    break
        # 2. 종목명으로 검색하는 경우 (대소문자, 띄어쓰기 무시)
        else:
            search_key = user_input.upper().replace(" ", "")
            for name, code in ticker_dict.items():
                if name.upper().replace(" ", "") == search_key:
                    ticker = code
                    stock_name = name # 정확한 공식 명칭으로 덮어쓰기
                    break
                    
        if not ticker:
            st.error(f"'{user_input}' 종목을 찾을 수 없습니다. 정확한 이름이나 6자리 종목코드를 입력해주세요.")
            st.stop()
            
        st.success(f"종목 확인 완료: **{stock_name}** ({ticker})")
        
        with st.spinner("네이버 증권에서 재무 데이터 실시간 로딩 중..."):
            try:
                naver_api = NaverFinanceApi()
                stock_data = naver_api.get_stock_data(ticker)
                
                # Display metrics nicely in cards
                st.subheader("📊 핵심 재무 지표")
                cols = st.columns(4)
                
                # Helper function to format numbers safely
                def format_num(val):
                    if not val or val == 'N/A': return 'N/A'
                    try: return f"{int(float(val)):,}"
                    except: return str(val)
                
                cols[0].metric("현재가", f"{format_num(stock_data.get('현재가', 0))} 원")
                cols[1].metric("PER", stock_data.get('PER', 'N/A'))
                cols[2].metric("PBR", stock_data.get('PBR', 'N/A'))
                cols[3].metric("EPS", f"{format_num(stock_data.get('EPS', 0))} 원")
                
            except Exception as e:
                st.error(f"데이터 연동 실패: {e}")
                st.stop()
                
        with st.spinner("최근 1년 주가 차트 생성 중..."):
            try:
                import datetime
                start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
                df_chart = fdr.DataReader(ticker, start_date)
                if not df_chart.empty:
                    st.subheader("📉 최근 1년 주가 흐름")
                    st.line_chart(df_chart['Close'], use_container_width=True)
            except Exception as e:
                pass # 차트 실패시 그냥 넘어감
                
        with st.spinner("AI(Gemini)가 업황과 해외매출 가능성 등을 분석 중입니다... (10~20초 소요)"):
            try:
                analyzer = StockAnalyzer(gemini_api_key)
                report = analyzer.analyze(stock_name, stock_data)
                
                st.markdown("---")
                st.subheader("💡 AI 종합 분석 결과")
                
                # Display markdown report inside a container with some styling
                with st.container(border=True):
                    st.markdown(report)
                    
                # Add a download button for the report
                st.download_button(
                    label="📥 분석 보고서 다운로드 (텍스트 파일)",
                    data=report,
                    file_name=f"{stock_name}_AI분석리포트.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                    
            except Exception as e:
                st.error(f"AI 분석 실패: {e}")

import os
from google import genai
from google.genai import types

class StockAnalyzer:
    def __init__(self, api_key):
        # Initialize Gemini Client
        self.client = genai.Client(api_key=api_key)
        # Use the latest 3.6 flash model
        self.model_id = 'gemini-3.6-flash' 

    def analyze(self, stock_name, stock_data):
        news_text = "\n".join(stock_data.get('최근뉴스', []))
        prompt = f"""
당신은 최고의 대한민국 주식 전문 수석 애널리스트입니다. 아래 제공된 기업의 실시간 시세, 밸류에이션, 최근 4개년 연간/분기 재무제표, 라이벌 경쟁사, 최근 뉴스 데이터를 철저히 검토하고 입체적이고 날카로운 종합 분석 리포트를 작성해주세요.

종목명: {stock_name}

[1. 기본 시세 및 수급 데이터]
- 현재가: {stock_data.get('현재가')} 원 (52주 최고/최저: {stock_data.get('52주최고최저', 'N/A')})
- 시가총액: {stock_data.get('시가총액')}
- PER: {stock_data.get('PER')} / PBR: {stock_data.get('PBR')} / EPS: {stock_data.get('EPS')}원
- 외국인 지분율: {stock_data.get('외국인소진율', 'N/A')}
- 배당수익률: {stock_data.get('배당수익률', 'N/A')}%
- 증권사 컨센서스: {stock_data.get('목표주가', '컨센서스 없음')} (추정 PER: {stock_data.get('추정PER', 'N/A')}, 추정 EPS: {stock_data.get('추정EPS', 'N/A')})

[2. 연간 재무제표 (기업실적 및 건전성 추이)]
{stock_data.get('연간재무제표', '연간 재무제표 데이터 없음')}

[3. 최근 분기 재무제표]
{stock_data.get('분기재무제표', '분기 재무제표 데이터 없음')}

[4. 동일업종 주요 경쟁사]
{stock_data.get('동일업종비교', '경쟁사 정보 없음')}

[5. 최근 주요 뉴스 헤드라인]
{news_text}

---
위 데이터를 바탕으로 다음 목차에 따라 심층적으로 분석하고 마크다운(Markdown) 보고서로 출력해주세요:

### 1. 📊 재무제표 및 재무건전성 분석 (핵심)
- **실적 성장성**: 최근 수년간 매출액, 영업이익, 당기순이익의 증가/감소 추이 및 흑자/적자 분석
- **수익성**: 영업이익률 및 순이익률의 개선 여부
- **재무건전성**: 부채비율(안정권인지 과다 부채인지), 당좌비율(단기 유동성), 유보율(사내 잉여금)을 종합하여 부도/유상증자 리스크 및 건전성 진단

### 2. 💎 밸류에이션 및 가격 위치
- PER, PBR, 52주 고점 대비 현재가 낙폭을 고려한 저평가/고평가 상태 분석

### 3. 🥊 동일업종 경쟁사 비교
- 동종업계 라이벌 기업들과 비교했을 때 실적이나 주가 매력도 평가

### 4. 🌊 업황 분석 (블루오션 vs 레드오션)
- 이 회사가 속한 섹터가 향후 급성장하는 유망 업황인지, 경쟁 과열 레드오션인지 분석

### 5. 🌏 해외 매출 및 글로벌 확장성
- 해외 수출 비중 확대 및 글로벌 시장에서의 경쟁력/수주 가능성 분석

### 6. 📰 최근 모멘텀 및 뉴스 이슈
- 최신 뉴스에 나타난 수주, 신사업, 악재 등 주가 모멘텀 해석

### 7. 🏆 최종 종합 등급 및 총평 (A ~ F)
- **최종 투자 매력도 등급**: [ A / B / C / D / E / F ] 중 하나 부여
- **핵심 이유 요약**: 등급 부여 이유를 명확하게 2줄로 총평

(주의: 불필요한 서론/결론은 생략하고, 각 항목별로 핵심만 2~3줄의 불릿포인트로 신속하고 명확하게 작성해주세요.)
"""

        import time

        last_error = None
        for attempt in range(2):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                err_str = str(e)
                if '503' in err_str or 'UNAVAILABLE' in err_str or '429' in err_str or 'high demand' in err_str:
                    time.sleep(1)
                    continue
                else:
                    raise e

        raise last_error

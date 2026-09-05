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
당신은 최고의 주식 애널리스트입니다. 아래의 한국 주식 종목과 최신 데이터를 바탕으로 회사를 입체적으로 평가해주세요.

종목명: {stock_name}

[재무 및 수급 데이터]
- 현재가: {stock_data.get('현재가')} 원 (52주 최고/최저: {stock_data.get('52주최고최저', 'N/A')})
- 시가총액: {stock_data.get('시가총액')} 억원
- PER / PBR / EPS: {stock_data.get('PER')} / {stock_data.get('PBR')} / {stock_data.get('EPS')}원
- 외국인 지분율: {stock_data.get('외국인소진율', 'N/A')}

[최근 주요 뉴스 헤드라인]
{news_text}

위 데이터를 바탕으로 다음 항목들을 분석하고, 최종적으로 A부터 F까지의 종합 등급을 부여해주세요.

1. **가치 및 수급 분석**: PER, PBR 등의 가치 평가와 외국인 지분율, 52주 주가 흐름을 종합하여 현재 주가의 위치를 평가하세요.
2. **모멘텀 및 이슈 분석 (뉴스 기반)**: 주어진 최근 뉴스 헤드라인을 바탕으로 이 회사에 수주, 실적 발표, 악재 등 어떤 모멘텀이 있는지 분석하세요.
3. **업황 전망 및 해외 매출 성장성**: 이 산업군이 레드오션인지 블루오션인지, 그리고 글로벌 경쟁력이 있는지 평가하세요.
4. **종합 판단 및 최종 등급 (A ~ F)**: 위 모든 것을 종합하여 최종 투자 매력도 등급(A, B, C, D, E, F)을 부여하고 핵심 이유를 한 줄로 요약하세요.

출력은 읽기 쉬운 마크다운(Markdown) 형식으로 작성해주세요.
"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )
        return response.text

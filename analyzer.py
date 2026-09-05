import os
from google import genai
from google.genai import types

class StockAnalyzer:
    def __init__(self, api_key):
        # Initialize Gemini Client
        self.client = genai.Client(api_key=api_key)
        # Use flash model to avoid strict rate limits on the free tier
        self.model_id = 'gemini-3.1-flash-preview' 

    def analyze(self, stock_name, stock_data):
        prompt = f"""
당신은 최고의 주식 애널리스트입니다. 아래의 한국 주식 종목과 재무 데이터를 바탕으로 회사를 종합적으로 평가해주세요.

종목명: {stock_name}

[재무 데이터 (한투 API 제공)]
- 현재가: {stock_data.get('현재가')} 원
- 시가총액: {stock_data.get('시가총액')} 억원
- PER (주가수익비율): {stock_data.get('PER')}
- PBR (주가순자산비율): {stock_data.get('PBR')}
- EPS (주당순이익): {stock_data.get('EPS')} 원

위 데이터를 바탕으로 다음 항목들을 분석하고, 최종적으로 A부터 F까지의 종합 등급을 부여해주세요.

1. **재무제표 및 재무건전성 분석**: 주어진 PER, PBR, EPS 등을 바탕으로 현재 주가가 고평가인지 저평가인지, 재무 상태가 건전한지 분석하세요.
2. **업황 전망 (레드오션 vs 블루오션)**: 이 회사가 속한 산업군이 앞으로 떠오르는 산업인지, 아니면 경쟁이 치열한 레드오션인지 당신의 지식을 바탕으로 평가하세요.
3. **해외 매출 성장 가능성**: 이 회사의 제품이나 서비스가 글로벌 시장에서 통할 수 있는지, 해외 매출이 늘어날 가능성이 있는지 분석하세요.
4. **종합 판단 및 최종 등급 (A ~ F)**: 위 모든 것을 종합하여 최종 투자 매력도 등급(A, B, C, D, E, F)을 부여하고 그 이유를 한 줄로 요약하세요. A는 강력 매수, F는 절대 매도입니다.

출력은 읽기 쉬운 마크다운(Markdown) 형식으로 작성해주세요.
"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )
        return response.text

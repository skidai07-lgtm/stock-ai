import requests
from bs4 import BeautifulSoup

class NaverFinanceApi:
    def get_stock_data(self, ticker):
        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            raise Exception(f"Failed to fetch data from Naver Finance (Status: {res.status_code})")
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        data = {}
        
        try:
            # 현재가
            price_div = soup.select_one('.no_today .blind')
            if price_div:
                data['현재가'] = price_div.text.replace(',', '')
                
            # 시가총액 (억)
            market_cap_em = soup.select_one('#_market_sum')
            if market_cap_em:
                data['시가총액'] = market_cap_em.text.replace(',', '').replace('\t', '').replace('\n', '')
                
            # 투자정보 테이블 (PER, EPS, PBR, BPS 등)
            # 네이버 금융 우측 펀더멘털 테이블 파싱
            per_em = soup.select_one('#_per')
            if per_em: data['PER'] = per_em.text
            
            eps_em = soup.select_one('#_eps')
            if eps_em: data['EPS'] = eps_em.text.replace(',', '')
            
            pbr_em = soup.select_one('#_pbr')
            if pbr_em: data['PBR'] = pbr_em.text
            
            bps_em = soup.select_one('#_bps')
            if bps_em: data['BPS'] = bps_em.text.replace(',', '')
            
            div_em = soup.select_one('#_dvr')
            if div_em: data['배당수익률'] = div_em.text
            
        except Exception as e:
            print(f"Parsing error: {e}")
            
        return data

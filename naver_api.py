import requests
from bs4 import BeautifulSoup

class NaverFinanceApi:
    def get_stock_data(self, ticker):
        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            raise Exception(f"Failed to fetch data from Naver Finance (Status: {res.status_code})")
            
        soup = BeautifulSoup(res.text, 'html.parser')
        data = {}
        
        try:
            # 기본 가격 및 시가총액
            price_div = soup.select_one('.no_today .blind')
            if price_div: data['현재가'] = price_div.text.replace(',', '')
            
            market_cap_em = soup.select_one('#_market_sum')
            if market_cap_em: data['시가총액'] = market_cap_em.text.replace(',', '').strip()
                
            # 펀더멘털 (PER, EPS, PBR, BPS)
            per_em = soup.select_one('#_per')
            if per_em: data['PER'] = per_em.text
            
            eps_em = soup.select_one('#_eps')
            if eps_em: data['EPS'] = eps_em.text.replace(',', '')
            
            pbr_em = soup.select_one('#_pbr')
            if pbr_em: data['PBR'] = pbr_em.text
            
            # 외국인 지분율
            foreign_ratio = soup.select_one('.lwidth tbody tr:nth-of-type(3) td em')
            if foreign_ratio: data['외국인소진율'] = foreign_ratio.text
            
            # 52주 최고/최저
            high52 = soup.select_one('.rwidth tbody tr:nth-of-type(2) td em:nth-of-type(1)')
            low52 = soup.select_one('.rwidth tbody tr:nth-of-type(2) td em:nth-of-type(2)')
            if high52 and low52: data['52주최고최저'] = f"{high52.text} / {low52.text}"
            
            # 동일업종 PER (경쟁사 대비 고평가/저평가 판단용)
            industry_per = soup.select_one('table.summary_info tr:nth-of-type(6) td em')
            if not industry_per:
                industry_per = soup.select_one('#_cmp_per')
            if industry_per: data['동일업종PER'] = industry_per.text
            
            # 배당수익률
            div_em = soup.select_one('#_dvr')
            if div_em: data['배당수익률'] = div_em.text

            # 최근 뉴스 헤드라인 추출 (수주, 호재, 악재 파악용)
            news_list = []
            news_tags = soup.select('.news_section ul.spt_con li a.tit')
            for tag in news_tags[:5]: # 최대 5개까지만
                news_list.append(tag.text.strip())
            data['최근뉴스'] = news_list if news_list else ["최근 주요 뉴스가 없습니다."]
            
        except Exception as e:
            print(f"Parsing error: {e}")
            
        return data

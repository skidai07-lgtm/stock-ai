import os
import requests
from pykrx import stock

class KisApi:
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        res = requests.post(url, headers=headers, json=body)
        if res.status_code == 200:
            return res.json().get("access_token")
        else:
            raise Exception(f"Failed to get KIS access token: {res.text}")

    def get_stock_data(self, ticker):
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100" # 주식현재가 시세
        }
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": ticker
        }
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json().get('output', {})
            return {
                "현재가": data.get("stck_prpr"),
                "PER": data.get("per"),
                "PBR": data.get("pbr"),
                "EPS": data.get("eps"),
                "BPS": data.get("bps"),
                "시가총액": data.get("hts_avls") # 단위: 억
            }
        else:
            raise Exception(f"Failed to get stock data: {res.text}")

def get_ticker_by_name(name):
    # 오늘 날짜 기준으로 상장된 종목들의 티커를 가져옴 (pykrx 사용)
    # pykrx는 날짜를 요구하므로 최근 영업일을 구하는 로직이 필요하지만, 
    # 간단히 stock.get_market_ticker_list()를 사용해도 됨
    
    # 코스피, 코스닥 종목 검색
    for market in ["KOSPI", "KOSDAQ"]:
        tickers = stock.get_market_ticker_list(market=market)
        for ticker in tickers:
            stock_name = stock.get_market_ticker_name(ticker)
            if name == stock_name:
                return ticker
    return None

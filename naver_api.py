import requests

class NaverFinanceApi:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_stock_data(self, ticker):
        data = {}

        # 1. 기본 시세, 밸류에이션, 수급 데이터 (Integration API)
        try:
            url = f"https://m.stock.naver.com/api/stock/{ticker}/integration"
            r = requests.get(url, headers=self.headers, timeout=6)
            if r.status_code == 200:
                d = r.json()
                for info in d.get("totalInfos", []):
                    code = info.get("code")
                    val = str(info.get("value", "N/A")).replace("배", "").replace("원", "").strip()
                    if code == "lastClosePrice": data["현재가"] = val
                    elif code == "marketValue": data["시가총액"] = val
                    elif code == "foreignRate": data["외국인소진율"] = val
                    elif code == "highPriceOf52Weeks": data["52주최고"] = val
                    elif code == "lowPriceOf52Weeks": data["52주최저"] = val
                    elif code == "per": data["PER"] = val
                    elif code == "pbr": data["PBR"] = val
                    elif code == "eps": data["EPS"] = val
                    elif code == "bps": data["BPS"] = val
                    elif code == "dividendYieldRatio": data["배당수익률"] = val
                    elif code == "cnsPer": data["추정PER"] = val
                    elif code == "cnsEps": data["추정EPS"] = val

                high = data.get("52주최고", "N/A")
                low = data.get("52주최저", "N/A")
                data["52주최고최저"] = f"{high} / {low}"

                # 증권사 목표주가 및 투자의견 컨센서스
                cns = d.get("consensusInfo")
                if cns:
                    target_price = cns.get("targetPrice", "N/A")
                    opinion = cns.get("consensusName", "N/A")
                    data["목표주가"] = f"{target_price}원 (투자의견: {opinion})"

                # 동일업종 경쟁사 비교
                peers = d.get("industryCompareInfo", [])
                peer_list = []
                for p in peers[:4]:
                    p_name = p.get("stockName")
                    p_price = p.get("closePrice")
                    p_fluc = p.get("fluctuationsRatio")
                    peer_list.append(f"- {p_name}: 현재가 {p_price}원 (등락률: {p_fluc}%)")
                if peer_list:
                    data["동일업종비교"] = "\n".join(peer_list)
        except Exception as e:
            print("Integration API error:", e)

        # 2. 연간 재무제표 (매출액, 영업이익, 순이익, ROE, 부채비율, 당좌비율, 유보율 등)
        try:
            url = f"https://m.stock.naver.com/api/stock/{ticker}/finance/annual"
            r = requests.get(url, headers=self.headers, timeout=6)
            if r.status_code == 200:
                fin_info = r.json().get("financeInfo", {})
                titles = [t.get("title") for t in fin_info.get("trTitleList", [])]
                keys = [t.get("key") for t in fin_info.get("trTitleList", [])]

                lines = ["[기준년도 | " + " | ".join(titles) + "]"]
                for row in fin_info.get("rowList", []):
                    r_title = row.get("title")
                    vals = [str(row.get("columns", {}).get(k, {}).get("value", "-")) for k in keys]
                    lines.append(f"- {r_title}: " + " | ".join(vals))
                data["연간재무제표"] = "\n".join(lines)
        except Exception as e:
            print("Annual finance API error:", e)

        # 3. 최근 분기 재무제표
        try:
            url = f"https://m.stock.naver.com/api/stock/{ticker}/finance/quarter"
            r = requests.get(url, headers=self.headers, timeout=6)
            if r.status_code == 200:
                fin_info = r.json().get("financeInfo", {})
                titles = [t.get("title") for t in fin_info.get("trTitleList", [])]
                keys = [t.get("key") for t in fin_info.get("trTitleList", [])]

                lines = ["[기준분기 | " + " | ".join(titles) + "]"]
                for row in fin_info.get("rowList", []):
                    r_title = row.get("title")
                    vals = [str(row.get("columns", {}).get(k, {}).get("value", "-")) for k in keys]
                    lines.append(f"- {r_title}: " + " | ".join(vals))
                data["분기재무제표"] = "\n".join(lines)
        except Exception as e:
            print("Quarter finance API error:", e)

        # 4. 최근 뉴스 5개
        try:
            url = f"https://m.stock.naver.com/api/news/stock/{ticker}?page=1&pageSize=5"
            r = requests.get(url, headers=self.headers, timeout=6)
            if r.status_code == 200:
                res_json = r.json()
                if isinstance(res_json, list) and len(res_json) > 0:
                    items = res_json[0].get("items", [])
                    news_titles = [item.get("titleFull") or item.get("title") for item in items[:5]]
                    data["최근뉴스"] = news_titles if news_titles else ["최근 뉴스가 없습니다."]
        except Exception as e:
            print("News API error:", e)

        if "최근뉴스" not in data:
            data["최근뉴스"] = ["최근 뉴스가 없습니다."]

        return data

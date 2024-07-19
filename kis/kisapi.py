'''
한국투자증권 python
'''
import datetime
import json
import os

import pandas as pd
import requests
import time

class KISAPI:
    '''
    koreainvestment
    한국투자증권 REST API
    '''
    def __init__(self, api_key: str, api_secret: str, acc_no: str, isvts: bool = False):
        """
        Name:생성자
        Args:
            api_key (str): 발급받은 API key
            api_secret (str): 발급받은 API secret
            acc_no (str): 계좌번호 체계의 앞 8자리-뒤 2자리
            vts (bool): True (모의투자), False (실전투자)
        """
        self.isvts = isvts
        self.set_base_url(isvts)
        self.api_key = api_key
        self.api_secret = api_secret

        # account number
        self.acc_no = acc_no
        self.acc_no_prefix = acc_no.split('-')[0]
        self.acc_no_postfix = acc_no.split('-')[1]
        self.authorization = ""
        self.access_token = ""

        # access token, authorization 
        # self.get_access_token()

    def set_base_url(self, isvts: bool = True):
        """
        Name:모의투자/실전투자 url 지정
        Args:
            isvts(bool, optional): True: 테스트서버, False: 실서버 Defaults to True.
        """
        if isvts:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
        else:
            self.base_url = "https://openapi.koreainvestment.com:9443"

    # OAuth인증

    def get_hashkey(self, data: dict):
        """
        Name:Hashkey
        Args:
            data (dict): POST 요청 데이터
        Returns:
            haskkey
        """
        path = "uapi/hashkey"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "User-Agent": "Mozilla/5.0"
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        haskkey = resp.json()["HASH"]
        return haskkey
    
    def get_access_token(self):
        """
        Name:접근토큰발급
        """
        path = "oauth2/tokenP"
        url = f"{self.base_url}/{path}"

        headers = {"content-type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.api_key,
            "appsecret": self.api_secret
        }

        # json 에 바로 data를 지정해도 된다.
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        # print(resp.text)
        # resp = requests.post(url, headers=headers, json=data)

        # 토큰 추출
        resp_access_token = resp.json()["access_token"]
        # print(resp_access_token)
        # resp_data = resp.json()

        # header에 지정할 때 Bearer를 추가 해야 하는데 여기서 한다.
        # self.access_token = f'Bearer {resp_data["access_token"]}'
        self.authorization = f'Bearer {resp_access_token}'
        self.access_token = resp_access_token
        return
    
    def del_access_token(self):
        """
        Name:접근토큰폐기
        """
        path = "oauth2/revokeP"
        url = f"{self.base_url}/{path}"

        headers = {"content-type": "application/json"}
        data = {
            "appkey": self.api_key,
            "appsecret": self.api_secret,
            "token":self.access_token
        }

        # json 에 바로 data를 지정해도 된다.
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        data = resp.json()
        self.authorization = ""
        self.access_token = ""
        return


    # [국내주식] 기본시세
    def get_domestic_price(self, symbol: str) -> dict:
        """
        Name:주식현재가 시세
        Args:
            symbol (str): 종목코드 6자리 스트링

        Returns:
            dict: API 개발 가이드 참조
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.authorization,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST01010100"
        }
        # fid_cond_mrkt_div_code
        # J : 주식, ETF, ETN
        # W : ELW
        # fid_input_iscd 종목번호 6자리
        # 삼성전자 005930
        # TIGER 미국 S&P500  360750
        # KODEX 200 0659500
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()
    
    def _get_domestic_daily_price(self, symbol: str, timeframe: str = 'D') -> dict:
        """
        Name:주식현재가 일자별
        Args:
            symbol (str): 종목코드
            timeframe (str): "D" (30 일), "W" (30 주), "M" (30 월)
        Returns:
            dict: _description_
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.authorization,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST01010400"
        }
        # fid_org_adj_prc
        # 0 : 수정주가반영
        # 1 : 수정주가미반영
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
            "fid_org_adj_prc": "0",
            "fid_period_div_code": timeframe
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()
    
    def get_domestic_D30_price(self, symbol: str) -> dict:
        """
        Name:주식현재가 일자별 변형 30일 (일봉 30개)
        Args:
            symbol (str): 종목코드
        Returns:
            dict: _description_
        """
        resp = self._get_domestic_daily_price(symbol,"D")
        return resp
    
    def get_domestic_W30_price(self, symbol: str) -> dict:
        """
        Name:주식현재가 일자별 변형 30주 (주봉 30개)
        Args:
            symbol (str): 종목코드
        Returns:
            dict: _description_
        """
        resp = self._get_domestic_daily_price(symbol,"W")
        return resp
    
    def get_domestic_M30_price(self, symbol: str) -> dict:
        """
        Name:주식현재가 일자별 변형 30월 (월봉 30개)
        Args:
            symbol (str): 종목코드
        Returns:
            dict: _description_
        """
        resp = self._get_domestic_daily_price(symbol,"M")
        return resp

    # [국내주식] 주문/계좌
    def _get_domestic_balance(self, ctx_area_fk100: str = "", ctx_area_nk100: str = "") -> dict:
        """
        Name:주식잔고조회
        Args:
            ctx_area_fk100 (str): 연속조회검색조건100
            공란 : 최초 조회시 
            이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
            ctx_areak_nk100 (str): 연속조회키100
        Returns:
            실전: 최대 50건 이후 연속조회
            모의: 최대 20건 이후 연속조회
            dict: _description_
        """
        path = "uapi/domestic-stock/v1/trading/inquire-balance"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.authorization,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "VTTC8434R" if self.isvts else "TTTC8434R"
        }
        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            'AFHR_FLPR_YN': 'N',
            'OFL_YN': 'N',
            'INQR_DVSN': '02', # INQR_DVSN 01: 대출일별, 02:종목별
            'UNPR_DVSN': '01',
            'FUND_STTL_ICLD_YN': 'N',
            'FNCG_AMT_AUTO_RDPT_YN': 'N',
            'PRCS_DVSN': '01',
            'CTX_AREA_FK100': ctx_area_fk100,
            'CTX_AREA_NK100': ctx_area_nk100
        }

        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        # tr_cont 연속 거래 여부
        # F or M : 다음 데이터 있음
        # D or E : 마지막 데이터
        data['tr_cont'] = res.headers['tr_cont']
        return data

    def get_domestic_balance(self) -> dict:
        """
        Name:주식잔고조회

        Args:

        Returns:
            dict: response data
        """
        output = {}

        data = self._get_domestic_balance()
        # output1 종목별 정보
        # output2 계좌 정보
        # output2 > dnca_tot_amt : 예수금
        # output2 > nxdy_excc_amt : 예수금 D + 1
        # output2 > prvs_rcdl_excc_amt : 예수금 D + 2 > 매수가능금액

        output['output1'] = data['output1']
        output['output2'] = data['output2']

        while data['tr_cont'] == 'M':
            fk100 = data['ctx_area_fk100']
            nk100 = data['ctx_area_nk100']

            data = self._get_domestic_balance(fk100, nk100)
            output['output1'].extend(data['output1'])
            output['output2'].extend(data['output2'])

        return output
    
    def get_domestic_psbl_order(self, symbol: str, price: int, order_type: str):
        """
        Name:매수가능조회
        Args:
            symbol (str): symbol
            price (int): 1주당 가격
            order_type (str): "00": 지정가, "01": 시장가, ..., "80": 바스켓
        """
        path = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.authorization,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "VTTC8908R" if self.isvts else "TTTC8908R"
        }
        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            'PDNO': symbol,
            'ORD_UNPR': str(price),
            'ORD_DVSN': order_type,
            'CMA_EVLU_AMT_ICLD_YN': '1',
            'OVRS_ICLD_YN': '1'
        }

        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        data['tr_cont'] = res.headers['tr_cont']
        return data
    
    def get_domestic_psbl_sell(self, symbol: str):
        """
        Name:매도가능수량조회
        모의투자 미지원
        Args:
            symbol (str): symbol 보유종목 코드
        """
        path = "/uapi/domestic-stock/v1/trading/inquire-psbl-sell"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.authorization,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "TTTC8408R" #모의투자 미지원
        }
        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            'PDNO': symbol
        }

        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        # ord_psbl_qty 에서 확인 가능
        return data
    
    def _set_domestic_order_cash(self, side: str, symbol: str, price: int,
                     quantity: int, order_type: str) -> dict:
        """
        Name:주식주문(현금)

        Args:
            side (str): _description_
            symbol (str): symbol
            price (int): _description_
            quantity (int): _description_
            order_type (str): _description_

        Returns:
            dict: _description_
        """
        path = "uapi/domestic-stock/v1/trading/order-cash"
        url = f"{self.base_url}/{path}"

        if self.isvts:
            tr_id = "VTTC0802U" if side == "buy" else "VTTC0801U"
        else:
            tr_id = "TTTC0802U" if side == "buy" else "TTTC0801U"

        unpr = "0" if order_type == "01" else str(price)

        data = {
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
            "PDNO": symbol,
            "ORD_DVSN": order_type,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": unpr
        }
        hashkey = self.get_hashkey(data)
        headers = {
           "content-type": "application/json",
           "authorization": self.authorization,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": tr_id,
           "custtype": "P",
           "hashkey": hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def set_market_price_buy_order(self, symbol: str, quantity: int) -> dict:
        """
        Name:시장가 매수

        Args:
            symbol (str): symbol
            quantity (int): quantity

        Returns:
            dict: _description_
        """
        resp = self._set_domestic_order_cash("buy", symbol, 0, quantity, "01")
        return resp

    def set_market_price_sell_order(self, symbol: str, quantity: int) -> dict:
        """
        Name:시장가 매도

        Args:
            symbol (str): _description_
            quantity (int): _description_

        Returns:
            dict: _description_
        """
        resp = self._set_domestic_order_cash("sell", symbol, 0, quantity, "01")
        
        return resp

    def set_limit_price_buy_order(self, symbol: str, price: int, quantity: int) -> dict:
        """
        Name:지정가 매수

        Args:
            symbol (str): 종목코드
            price (int): 가격
            quantity (int): 수량

        Returns:
            dict: _description_
        """
        resp = self._set_domestic_order_cash("buy", symbol, price, quantity, "00")
        
        return resp

    def set_limit_price_sell_order(self, symbol: str, price: int, quantity: int) -> dict:
        """
        Name:지정가 매도

        Args:
            symbol (str): _description_
            price (int): _description_
            quantity (int): _description_

        Returns:
            dict: _description_
        """
        resp = self._set_domestic_order_cash("sell", symbol, price, quantity, "00")
        return resp
    
    # close_price 현재가 또는 종가
    # hoga : 1 현재가 + 1호가
    # hoga + -2 현재가 - 2호가
    # 호가 기준
    # 2,000원 미만 1원
    # 2,000원 이상  5,000원 미만 5원
    # 5,000원 이상  20,000원 미만 10원
    # 20,000원 이상  50,000원 미만 50원
    # 50,000원 이상  200,000원 미만 100원
    # 200,000원 이상  500,000원 미만 500원
    # 500,000원 이상 1,000원
    # 
    # 경계에 있는 가격은 조심해야 할 것 같지만 고려하지 않았다.
    def calculate_order_price(self, close_price:int, hoga:int) -> int:
        order_price = 0
        if close_price < 2000:
            order_price = close_price + hoga * 1
            if order_price > 2000:
                last_digit = order_price % 10
                if last_digit == 0:
                    pass
                else:
                    order_price = order_price - last_digit + 10
                
        elif close_price < 5000:
            order_price = close_price + hoga * 5
            if order_price > 5000:
                last_digit = order_price % 10
                if last_digit == 0:
                    pass
                else:
                    order_price = order_price - last_digit + 10

        elif close_price < 20000:
            order_price = close_price + hoga * 10
            
            if order_price > 20000:
                last_digit = order_price % 100
                if last_digit == 0:
                    pass
                else:
                    order_price = order_price - last_digit + 100

        elif close_price < 50000:
            order_price = close_price + hoga * 50

            if order_price > 50000:
                last_digit = order_price % 100
                if last_digit == 0:
                    pass
                else:
                    order_price = order_price - last_digit + 100

        elif close_price < 200000:
            order_price = close_price + hoga * 100

            if order_price > 200000:
                last_digit = order_price % 1000
                if last_digit == 0:
                    pass
                else:
                    order_price = order_price - last_digit + 1000


        elif close_price < 500000:
            order_price = close_price + hoga * 500

            if order_price > 500000:
                last_digit = order_price % 1000
                if last_digit == 0:
                    pass
                else:
                    order_price = order_price - last_digit + 1000
        else:
            order_price = close_price + hoga * 1000

        

        return order_price


if __name__ == "__main__":
    ACCOUNT_NO_VTS = ""
    APP_KEY_VTS = ""
    APP_SECRET_VTS = ""

    key = APP_KEY_VTS
    secret = APP_SECRET_VTS
    acc_no = ACCOUNT_NO_VTS

    # mts 생성
    mts_kis = KISAPI(
        api_key=key,
        api_secret=secret,
        acc_no=acc_no,
        isvts=True
    )

    # 로그인
    mts_kis.get_access_token()
    time.sleep(1)

    # 작업
    # 잔고조회
    # balance = mts_kis.get_domestic_balance()
    # print(balance)
    # time.sleep(1)
    resjson = mts_kis.get_domestic_W30_price(symbol='360750')
    rt_cd = resjson['rt_cd']
    output = resjson['output']
    stck_oprc = output[0]['stck_oprc']
    stck_clpr = output[0]['stck_clpr']
    try:
        if rt_cd == '0':
            for v in output:
                # print(i)
                print(v)
        
        print(stck_oprc)
        print(stck_clpr)
        if int(stck_oprc) >= int(stck_clpr):
            print("음봉")
        else:
            print("양봉")
    except:
        print("except")
    

    # 로그아웃
    mts_kis.del_access_token()
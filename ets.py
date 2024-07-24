import threading
import time
from datetime import datetime

import os
from dotenv import load_dotenv

import schedule
from PIL import Image
from pystray import Icon, MenuItem, Menu

from kis import KISAPI
from util import PrettyJson

app_name = 'ets'

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
ACCOUNT_NO = os.getenv("ACCOUNT_NO")
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

ACCOUNT_NO_VTS = os.getenv("ACCOUNT_NO_VTS")
APP_KEY_VTS = os.getenv("APP_KEY_VTS")
APP_SECRET_VTS = os.getenv("APP_SECRET_VTS")

# 좋아하는 종목 다른 것으로 5가지 선택 할 것
# 월: TIGER 미국S&P500,360750
# 화: TIGER 미국필라델피아반도체나스,381180
# 수: TIGER 미국테크TOP10 INDXX,381170
# 목: KODEX 미국S&P500TR,379800
# 금: KODEX 미국나스닥100TR,379810
SIMBOL_LIST = ['360750','381180','381170','379800','379810']

class TaskTray:

    def __init__(self, image):
        self.status = False

        self.is_buy_enabled = True
        self.is_sell_enabled = True

        # 실전 매매
        self.key = APP_KEY
        self.secret = APP_SECRET
        self.acc_no = ACCOUNT_NO
        self.isvts = False

        # 모의 매매
        # self.key = APP_KEY_VTS
        # self.secret = APP_SECRET_VTS
        # self.acc_no = ACCOUNT_NO_VTS
        # self.isvts = True

        # mts 생성
        # isvts: 실전=False 모의=True
        self.mts_kis = KISAPI(
            api_key=self.key,
            api_secret=self.secret,
            acc_no=self.acc_no,
            isvts=self.isvts
        )

        image = Image.open(image)
        # 트레이에 상주하는 앱 아이콘을 오른쪽 클릭했을 때의 메뉴 설정
        menu = Menu(
            MenuItem('매수 ON', self.toggle_buy_enabled, checked=self.getchecked_buy_on()),
            MenuItem('매수 OFF', self.toggle_buy_disabled, checked=self.getchecked_buy_off()),
            MenuItem('매도 ON', self.toggle_sell_enabled, checked=self.getchecked_sell_on()),
            MenuItem('매수 OFF', self.toggle_sell_disabled, checked=self.getchecked_sell_off()),
            MenuItem('', None, enabled=False),
            MenuItem('잔고 확인', self.print_balance),
            MenuItem('1주 매수', self.do_buy_today),
            MenuItem('전종목 매도', self.do_sell_all),
            MenuItem('', None, enabled=False),
            MenuItem('종료', self.stop),
        )
        self.icon = Icon(name=app_name, title=app_name, icon=image, menu=menu)

    def run(self):
        self.status = True

        # 정기 실행 작업을 병렬 처리하여 실행 시작
        task_thread = threading.Thread(target=self.run_schedule)
        task_thread.start()

        self.icon.run()

    def run_schedule(self):
        # kisapi 실행 설정
        # 5종목 시스템 0,1,2,3,4
        schedule.every().monday.at("12:35").do(self.do_sell_weekday, i=0)
        schedule.every().monday.at("13:05").do(self.do_buy_weekday, i=0)
        schedule.every().tuesday.at("12:35").do(self.do_sell_weekday, i=1)
        schedule.every().tuesday.at("13:05").do(self.do_buy_weekday, i=1)
        schedule.every().wednesday.at("12:35").do(self.do_sell_weekday, i=2)
        schedule.every().wednesday.at("13:05").do(self.do_buy_weekday, i=2)
        schedule.every().thursday.at("12:35").do(self.do_sell_weekday, i=3)
        schedule.every().thursday.at("13:05").do(self.do_buy_weekday, i=3)
        schedule.every().friday.at("12:35").do(self.do_sell_weekday, i=4)
        schedule.every().friday.at("13:05").do(self.do_buy_weekday, i=4)

        while self.status:
            # 작업실행
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.status = False
        self.icon.stop()
    
    def getchecked_buy_on(self):
        def inner(item):
            return self.is_buy_enabled == True
        return inner
    
    def getchecked_buy_off(self):
        def inner(item):
            return self.is_buy_enabled == False
        return inner
    
    def getchecked_sell_on(self):
        def inner(item):
            return self.is_sell_enabled == True 
        return inner
    
    def getchecked_sell_off(self):
        def inner(item):
            return self.is_sell_enabled == False 
        return inner
    
    def toggle_buy_enabled(self):
        self.is_buy_enabled = True
    
    def toggle_buy_disabled(self):
        self.is_buy_enabled = False
    
    def toggle_sell_enabled(self):
        self.is_sell_enabled = True
    
    def toggle_sell_disabled(self):
        self.is_sell_enabled = False

    def is_good_for_buy(self, symbol:str) -> bool:
        try:
            # 양봉이면 매수 ok, 음봉이면 매수 ng
            resjson = self.mts_kis.get_domestic_W30_price(symbol)
            rt_cd = resjson['rt_cd']
            output = resjson['output']
            open_0w = output[0]['stck_oprc']
            close_0w = output[0]['stck_clpr']
            open_1w = output[1]['stck_oprc']
            close_1w = output[1]['stck_clpr']

            if rt_cd == '0' and int(open_0w) >= int(close_0w):
                print("bad for buy 0w")
                return False
            elif rt_cd == '0' and int(open_1w) >= int(close_1w):
                print("bad for buy 1w")
                return False
            else:
                print("good for buy")
                return True
        except:
            print("bad for buy exception")
            return False

    def is_good_for_buy_sys01_5w_under(self, symbol:str) -> bool:
        try:
            # output의 갯수가 25개이상이면 ok
            # 5주 평균 보다 낮고 30 평균보다 높으면 ok
            # 과거 20주 평균보다 현재 20주 평균이 높으면 ok
            resjson = self.mts_kis.get_domestic_W30_price(symbol)
            rt_cd = resjson['rt_cd']

            # response ng
            if rt_cd != '0' :
                print("bad for buy rt_cd")
                return False
            
            output = resjson['output']
            count = len(output)

            # output의 갯수가 25개이상이면 ok
            if(count < 25):
                print("bad for buy rt_cd")
                return False
            
            first_5_items = output[:5]
            first_20_items = output[:20]
            first_last_items = output[-20:]
            
            sum_clpr_all = sum(int(item["stck_clpr"]) for item in output)
            sum_clpr_first_5w = sum(int(item["stck_clpr"]) for item in first_5_items)
            sum_clpr_first_20w = sum(int(item["stck_clpr"]) for item in first_20_items)
            sum_clpr_las_20w = sum(int(item["stck_clpr"]) for item in first_last_items)

            avg_clpr_all = sum_clpr_all / count
            avg_clpr_first_5w = sum_clpr_first_5w / 5
            avg_clpr_first_20w = sum_clpr_first_20w / 20
            avg_clpr_last_20w = sum_clpr_las_20w / 20

            close_0w = float(output[0]['stck_clpr'])

            # 현재가가 5주 평균 보다 낮고 
            # 현재가가 30 평균보다 높고
            # 과거 20주 평균보다 현재 20주 평균이 높으면 ok
            if close_0w < avg_clpr_first_5w and close_0w > avg_clpr_all and avg_clpr_first_20w > avg_clpr_last_20w:
                print("good for buy")
                return True
            else:
                print("bad for buy")
                return False
        except:
            print("bad for buy exception")
            return False

    def do_buy(self):
        if self.is_buy_enabled:
            print("do_buy")
            # 로그인
            self.mts_kis.get_access_token()
            time.sleep(1)

            # check logic 추가
            isGoodForBuy = self.is_good_for_buy(symbol='360750')
            time.sleep(1)

            # 작업 시장가매수
            # Tiger S&P 500 1주 종목코드=360750
            if isGoodForBuy:
                resp = self.mts_kis.set_market_price_buy_order(symbol='360750',quantity=1)
                time.sleep(1)

            # 로그아웃
            self.mts_kis.del_access_token()
        
        return

    def do_buy_today(self):
        if self.is_buy_enabled:
            print("do_buy_today")
            # 로그인
            self.mts_kis.get_access_token()
            time.sleep(1)

            # check logic 없음 => 무조건 매수
            # 요일에 해당하는 종목 1주 매수
            # 오늘이 무슨 요일인지 숫자로 가져옵니다. (0 = 월요일, ..., 6 = 일요일)
            
            today_buy = datetime.today()
            weekday_num = today_buy.weekday()
            symbol_buy = SIMBOL_LIST[weekday_num]
        
            print(weekday_num)
            print(symbol_buy)

            # 현재가 조회
            resjson = self.mts_kis.get_domestic_W30_price(symbol_buy)
            rt_cd = resjson['rt_cd']

            # response ng
            if rt_cd != '0' :
                print("ng get_domestic_W30_price => market_price_buy")

                # 시장가매수
                time.sleep(1)
                resp = self.mts_kis.set_market_price_buy_order(symbol=symbol_buy,quantity=1)
                # print(resp)
                PrettyJson.pretty_print_json(resp)
            
            else:
                print("ok get_domestic_W30_price => limit_price_buy")
            
                output = resjson['output']
                # 현재가
                close_0w = int(output[0]['stck_clpr'])

                # 시장가로 주문하려면 상한가기준으로 예수금이 있어야 한다.
                # 그렇게 까지는 돈이 없으므로 2만원기준 5호가 정도 플러스 해줬다.
                # order_price = close_0w + 250
                # + 5호가
                order_price = self.mts_kis.calculate_order_price(close_0w,5)

                # 지정가 매수
                time.sleep(1)
                resp = self.mts_kis.set_limit_price_buy_order(symbol=symbol_buy,price=order_price,quantity=1)
                # print(resp)
                PrettyJson.pretty_print_json(resp)

            
            time.sleep(1)
            # 로그아웃
            self.mts_kis.del_access_token()

            
            print("do_buy_today finish")
        
        return

    def do_buy_weekday(self, i):
        print("do_buy_weekday")
        # i 0 ~ 4
        j = 0
        symbol_weeday = '360750'
        if (0 <= i <= 4): 
            j = i
            symbol_weeday = SIMBOL_LIST[j]

        if self.is_buy_enabled:
            # 로그인
            self.mts_kis.get_access_token()
            time.sleep(1)

            # check logic sys01
            # output의 갯수가 25개이상이면 ok
            # 5주 평균 보다 낮고 30 평균보다 높으면 ok
            # 과거 20주 평균보다 현재 20주 평균이 높으면 ok
            isGoodForBuy = self.is_good_for_buy_sys01_5w_under(symbol=symbol_weeday)
            time.sleep(1)

            # 작업 매수
            if isGoodForBuy:
                print("isGoodForBuy")
                # resp = self.mts_kis.set_market_price_buy_order(symbol=symbol_weeday,quantity=1)
                # time.sleep(1)
                
                # 현재가 조회
                resjson = self.mts_kis.get_domestic_W30_price(symbol_weeday)
                rt_cd = resjson['rt_cd']
                
                # response ng
                if rt_cd != '0' :
                    print("ng get_domestic_W30_price => market_price_buy")
                    # 시장가 매수
                    time.sleep(1)
                    resp = self.mts_kis.set_market_price_buy_order(symbol=symbol_weeday,quantity=1)
                else:
                    print("ok get_domestic_W30_price => limit_price_buy")
                    output = resjson['output']
                    # 현재가
                    close_0w = int(output[0]['stck_clpr'])
                    
                    # + 5호가
                    order_price = self.mts_kis.calculate_order_price(close_0w,5)
                    
                    # 지정가 매수
                    time.sleep(1)
                    resp = self.mts_kis.set_limit_price_buy_order(symbol=symbol_weeday,price=order_price,quantity=1)

            # 로그아웃
            time.sleep(1)
            self.mts_kis.del_access_token()
            print("do_buy_weekday finish")
        return

    def is_good_for_sell(self, symbol:str) -> int:
        try:
            # 매도 가능 수량이 0 보타 크고 평가손익률이 2.0 보다 크면 매도
            resjson = self.mts_kis.get_domestic_psbl_sell(symbol)
            # print(resjson)
            PrettyJson.pretty_print_json(resjson)

            #  "rt_cd": "0",
            rt_cd = resjson['rt_cd']
            output = resjson['output']
            # 주문가능수량  "ord_psbl_qty": "1744",
            ord_psbl_qty = output['ord_psbl_qty']
            # 평가손익율  "evlu_pfls_rt": "39.36"
            # int(float(value)) 소수점 이하 버림
            evlu_pfls_rt = output['evlu_pfls_rt']

            if rt_cd == '0' and int(ord_psbl_qty) > 0 and int(float(evlu_pfls_rt)) > 2 :
                print("good for sell")
                return int(ord_psbl_qty) 
            else:
                print("bad for sell")
                return 0
        except:
            print("bad for sell exception")
            return 0

    def is_good_for_sell_rate(self, symbol:str, target_rate:int) -> int:
        rate = 2
        if target_rate < 2 : rate = 2
        try:
            # 매도 가능 수량이 0 보타 크고 평가손익률이 2.0 보다 크면 매도
            resjson = self.mts_kis.get_domestic_psbl_sell(symbol)
            # print(resjson)
            PrettyJson.pretty_print_json(resjson)

            #  "rt_cd": "0",
            rt_cd = resjson['rt_cd']
            output = resjson['output']
            # 주문가능수량  "ord_psbl_qty": "1744",
            ord_psbl_qty = output['ord_psbl_qty']
            # 평가손익율  "evlu_pfls_rt": "39.36"
            # int(float(value)) 소수점 이하 버림
            evlu_pfls_rt = output['evlu_pfls_rt']

            if rt_cd == '0' and int(ord_psbl_qty) > 0 and int(float(evlu_pfls_rt)) > rate :
                print("good rate for sell")
                return int(ord_psbl_qty) 
            else:
                print("bad rate for sell")
                return 0
        except:
            print("bad rate for sell exception")
            return 0

    def do_sell_all(self):
        if self.is_sell_enabled:
            print("do_sell_all")

            # 로그인
            self.mts_kis.get_access_token()
            time.sleep(1)

            for i_symbol in SIMBOL_LIST:
                # 매도 가능 수량 확인
                resjson = self.mts_kis.get_domestic_psbl_sell(i_symbol)
                #  "rt_cd": "0",
                rt_cd = resjson['rt_cd']
                output = resjson['output']
                # 주문가능수량  "ord_psbl_qty": "1744",
                ord_psbl_qty = output['ord_psbl_qty']

                if rt_cd == '0' and int(ord_psbl_qty) > 0 :
                    time.sleep(1)
                    # 시장가매도
                    resp = self.mts_kis.set_market_price_sell_order(symbol=i_symbol,quantity=int(ord_psbl_qty))
                    
                time.sleep(1)

            time.sleep(1)
            # 로그아웃
            self.mts_kis.del_access_token()
        
        return

    def do_sell_weekday(self, i):
        print("do_sell_weekday")
        # i 0 ~ 4
        j = 0
        target_rate = 2
        symbol_weeday = '360750'
        if (0 <= i <= 4): 
            j = i
            # 목표수익률 2 ~ 8
            target_rate = (j + 1) * 2
            symbol_weeday = SIMBOL_LIST[j]

        if self.is_sell_enabled:
            # 로그인
            self.mts_kis.get_access_token()
            time.sleep(1)

            # check logic 추가
            isGoodForSellQty = 0
            intGoodForSellQty = self.is_good_for_sell_rate(symbol=symbol_weeday,target_rate=target_rate)
            time.sleep(1)

            # 작업 시장가매도
            # Tiger S&P 500 1주 종목코드=360750
            if intGoodForSellQty > 0:
                resp = self.mts_kis.set_market_price_sell_order(symbol=symbol_weeday,quantity=isGoodForSellQty)
                time.sleep(1)

            # 로그아웃
            self.mts_kis.del_access_token()
        
        return

    def print_balance(self):
        print("print_balance")

        # 로그인
        self.mts_kis.get_access_token()
        time.sleep(1)
        
        # 잔고조회
        balance = self.mts_kis.get_domestic_balance()
        PrettyJson.pretty_print_json(balance)
        time.sleep(1)

        # 로그아웃
        self.mts_kis.del_access_token()
        
        return

if __name__ == '__main__':
    system_tray = TaskTray(image='./favicon.ico')
    system_tray.run()

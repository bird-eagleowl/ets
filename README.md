# ets
eagleowl trading system  
한국투자증권 api를 이용해서 만드는 개인화된 나만의 트레이딩 시스템  
{사용자이름} trading system  
  
## work_2nd
ets 만들기
  
  
### 7 ets.exe 바로가기 만들고 윈도우 시작프로그램에 넣어주기   
바로가기를 만들어서 시작프로그램 폴더에 넣어주면 윈도우가 실행될때 자동으로 실행됩니다.  
  
./dist/ets.exe 오른쪽 클릭 => 바로가기 만들기  
  
윈도우10의 경우 아래 폴더에 바로가기 파일 복사 붙여 넣기  
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp  
  
실행후에 작업표시줄에 고정해주시면 추후에 직접 실행도 편합니다.  
  
### 6 .env, favicon.ico 파일 가져오기   
pyinstaller를 실행하면  
./dist/ets.exe 파일이 만들어진다.  
ets.exe 파일을 실행할때 필요한 파일인 .env, favicon.ico을 복사해서 ./dist폴더에 넣어주자.  
  
./.env => ./dist/.env 복사 붙여넣기  
./favicon.ico => ./dist/favicon.ico 복사 붙여넣기  
  
### 5 실행파일 만들기  
가상환경 실행후에 실행파일 만들기 명령어 입력  
pyinstaller --onefile --icon=favicon.ico ets.py  
  
cd ./venv/Scripts  
activate  
cd ../..  
pyinstaller --onefile --icon=favicon.ico ets.py  
...  
...  
...  
Building EXE from EXE-00.toc completed successfully.
  
### 4 ets.py 파일 만들기 또는 복사하기  
ets.py 파일 설명  
시작위치는 가장 하단의 '__main__'  
시작 클래스는 TaskTray  
시작 함수는 TaskTray의 run  
  
전체를 관리하는 클래스  
class TaskTray  
  
from kis import KISAPI  
kis의 KISAPI 생성해서 한투증권 api 사용하도록 구현  
  
from pystray import Icon, MenuItem, Menu  
pystray의 Icon, MenuItem, Menu를 이용해서 tray에서 실행 하도록 구현  
  
import threading  
run 함수에서 threading을 이용해서 일정 작업 등록 및 실행  
  
import schedule  
schedule을 이용해서 작업 일정 등록  
  
각종 함수  
  
def is_good_for_buy  
매수하면 좋을지 판단하는 함수  
양봉이면 매수 ok, 음봉이면 매수 ng  
  
def is_good_for_buy_sys01_5w_under  
주봉을 이용한 매수 판단 함수  
  
def do_buy  
시장가 매수 함수  
  
def do_buy_today  
오늘의 요일에 해당하는 종목 매수하는 함수  
  
def do_buy_weekday  
특정 요일에 해당하는 종목 매수하는 함수  
  
def is_good_for_sell  
매도 가능 확인 합수  
  
def is_good_for_sell_rate  
매도 가능 확인 합수 수익률 비교 포함  
  
def do_sell_all  
보유 종목 전체에 대해서 전량 시장가 매도 함수  
  
def do_sell_weekday  
특정 요일에 해당하는 종목 매도하는 함수  
  
def print_balance  
계좌 잔고 출력하는 함수  
    
    
### 3 favicon.ico 만들기 또는 복사하기  
트레이에서 보여줄 이미지 만들기 또는 복사하기  
48 x 48 ico 파일  
./favicon.ico  
  
### 2 util.py 만들기 또는 복사하기  
각종 편리한 기능 추가용 파일 (보기 편한 json 출력)  
./util 폴더 만들기  
./util/ets.py 파일 만들기  
./util/__init__.py 파일 만들기  
  
### 1 ets.py 기능 설명  
윈도우 트레이에서 존재해는 프로그램을 만들 것이다.  
트레이 메뉴를 통해서 조작할 수 있는 프로그램을 만들 것이다.  
예약된 시간에 동작하는 기능을 만들 것이다.  
진행상황이나 메시지등은 콘솔로 출력할 것이다.  
실행파일을 만들고 윈도우가 실행되면 자동 실행 되도록 할 것이다.  
  
## work_1st
시작하기  
  
### 6 kisapi 만들기 또는 복사하기
한국투자증권 REST API를 사용하기 위한 class  
./kis 폴더 만들기  
./kis/kisapi.py 만들기  
./kis/__init__.py 만들기(언더바언더바init언더바언더바.py)(언더바2개)  
./test_kis.py 만들고 실행해보기  
  
로그인 로그아웃 처리를 테스트 하면  
문제가 없는 경우 연결된 스마트폰으로 메시지가 온다  
"고객님의 명의 오픈API 접근토큰이 발급!!"  
"정상 발급인지 확인 바랍니다."  
  
### 5 .env 파일 만들기
./env 파일 작성  
아래는 필요한 내용이며 개발 중에 추가될 수 있다.  
app_key 발급 방법은 아래 url 참고  
https://apiportal.koreainvestment.com/intro  
https://wikidocs.net/book/7559  
  
ACCOUNT_NO = "계좌번호 전체 8자리-2자리 (예:12345678-01)"  
APP_KEY = "한국투자증권 홈페이지에서 발급받은 App Key"  
APP_SECRET = "한국투자증권 홈페이지에서 발급받은 App Secret"  
ACCOUNT_NO_VTS = "모의투자용 계좌번호 전체 8자리-2자리 (예:12345678-01)"  
APP_KEY_VTS = "모의투자용 App Key"  
APP_SECRET_VTS = "모의투자용 App Secret"  
  
### 4 test_print.py 로 실행 테스트 >> 기본 설정 완료  
./test_print.py 작성 하고 실행하기  
  
### 3 vscode 인터프리터 선택하기  
선택할 python 위치  
./venv/Scripts/pythone.exe  
ex)  
E:\work\ets\venv\Scripts\pythone.exe  
  
Ctrl + Shift + P  
Python Select Interpreter  
  
### 2 venv 패키지 설치 하기  
requirements.txt 참고해서 패키지를 설치한다.  
(잡스러운 것들이 포함되어서 조금 많다.)  
  
설치  
cd ./venv/Scripts  
activate  
cd ../..  
pip install -r requirements.txt  
  
추출  
cd ./venv/Scripts  
activate  
cd ../..  
pip freeze > requirements.txt  
  
### 1 venv 만들기   
OS: 윈도 10 (Windows 10)  
IDE: VScode (Visual Studio Code)  
python 버전: 3.12.2  
설치위치:~\AppData\Local\Programs\Python\Python312  
C:\Users\{사용자이름}\AppData\Local\Programs\Python\Python312  
가상환경: venv로 생성  
  
작업 폴더  
ex)  
E:\work\ets  
  
가상환경 폴더  
venv  
ex)  
E:\work\ets\venv  
  
venv 만들기 명령어  
C:\Users\{사용자이름}\AppData\Local\Programs\Python\Python312\python -m venv C:\{개발용Path}\venv  
  
ex)  
C:\Users\Eageleowl\AppData\Local\Programs\Python\Python312\python -m venv E:\work\ets\venv  
  
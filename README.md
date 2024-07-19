# ets
eagleowl trading system
한국투자증권 api를 이용해서 만드는 개인화된 나만의 트레이딩 시스템
{사용자이름} trading system

## work_1st
시작하기

### 6 kisapi 만들기 또는 복사하기
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

ACCOUNT_NO = "계좌번호 전체 8자리-2자리"
APP_KEY = "홈페이지에서 발급받은 App Key"
APP_SECRET = "홈페이지에서 발급받은 App Secret"
ACCOUNT_NO_VTS = "모의투자용 계좌번호 전체 8자리-2자리"
APP_KEY_VTS = "모의투자용 App Key"
APP_SECRET_VTS = "모의투자용 App Secret"

### 4 print.py 로 실행 테스트 >> 기본 설정 완료
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
import os
from dotenv import load_dotenv
from kis import KISAPI
import time

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
ACCOUNT_NO = os.getenv("ACCOUNT_NO")
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

ACCOUNT_NO_VTS = os.getenv("ACCOUNT_NO_VTS")
APP_KEY_VTS = os.getenv("APP_KEY_VTS")
APP_SECRET_VTS = os.getenv("APP_SECRET_VTS")

def main():
    print("test kis 입니다.")
    # kis 생성 실계좌
    ets_kis = KISAPI(
        api_key=APP_KEY,
        api_secret=APP_SECRET,
        acc_no=ACCOUNT_NO,
        isvts=True
    )

    # 로그인
    ets_kis.get_access_token()
    time.sleep(1)

    # 로그아웃
    ets_kis.del_access_token()


    return

if __name__ == '__main__':
    main()
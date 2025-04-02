import base64
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import re
import smtplib
import time
from pathlib import Path

import pandas as pd
import schedule



# SMTP 서버 설정
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "dmdals1012@gmail.com"
EMAIL_PASSWORD = "izrk dbhv sokt zwxy" 

try:
    print("📢 SMTP 서버 연결 시도 중 (TLS)...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # 보안 연결 활성화
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    print("✅ SMTP 로그인 성공!")
    server.quit()
except Exception as e:
    print(f"🚨 SMTP 로그인 실패: {str(e)}")



# 클러스터 그룹별 랜덤 이메일 선택 함수
def get_random_email_content(cluster_id):
    # 📌 CSV에서 매번 새롭게 불러오기 (랜덤화 유지)
    df = pd.read_csv('main/project_1/data_mini1/클러스터링_이메일_수정.csv')

    # 📌 클러스터 ID에 해당하는 이메일 필터링
    cluster_emails = df[df["Cluster ID"] == cluster_id][["Email Content", "Subject"]]

    if cluster_emails.empty:
        return "맞춤 프로모션 정보를 찾을 수 없습니다.", "제목 없음"

    # 📌 굵은 글씨 변환 (필터링 후 적용)
    cluster_emails["Email Content"] = cluster_emails["Email Content"].apply(lambda x: re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', x))

    # 📌 랜덤으로 하나 선택 후 반환
    selected_email = cluster_emails.sample(n=1).iloc[0]
    return selected_email["Email Content"], selected_email["Subject"]

def send_promotion_email(이메일, 이름, cluster_id):


    random_body, random_subject = get_random_email_content(cluster_id)

    
    # 이메일 제목
    subject = f"[프로모션] {random_subject}"

    # 이메일 본문 (이미지 포함)
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
        <table style="width: 100%; max-width: 800px; margin: auto; background: white; padding: 30px; 
                    border-radius: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.1);">
            <!-- 헤더 영역 (로고) -->
            <tr>
                <td style="text-align: center; padding: 20px; background: #005bac; color: white; 
                        border-top-left-radius: 15px; border-top-right-radius: 15px;">
                    <h1 style="margin: 0;">🚗 현대자동차 프로모션 🚗</h1>
                </td>
            </tr>
            
            <!-- 본문 내용 -->
            <tr>
                <td style="padding: 30px; text-align: center;">
                    
                    <!-- 현대 로고 -->
                    <a href="https://www.hyundai.com" target="_blank">
                    <img src="cid:hyundai_logo"
                        alt="현대 로고" style="width: 100%; max-width: 500px; border-radius: 10px;">
                    </a>

                    <p style="font-size: 18px;">안녕하세요, <strong>{이름}</strong>님!</p>

                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; font-size: 16px; margin-top: 20px;">
                        {random_body}
                    </div>
                    
                    <a href="https://www.hyundai.com" 
                        style="display: inline-block; background: #005bac; color: white; padding: 15px 30px; 
                            text-decoration: none; border-radius: 8px; margin-top: 20px; font-size: 16px;">
                        지금 확인하기
                    </a>
                </td>
            </tr>

            <!-- 푸터 (고객센터 안내) -->
            <tr>
                <td style="padding: 15px; font-size: 14px; text-align: center; color: gray;">
                    ※ 본 메일은 자동 발송되었으며, 문의는 고객센터를 이용해주세요.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    # 이메일 생성
    msg = MIMEMultipart()
    msg["From"] = "현대자동차"
    msg["To"] = 이메일
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

        # 로고 이미지 첨부 (CID 참조)
    with open("main/project_1/img/hyundai_logo.jpg", "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<hyundai_logo>")
        msg.attach(img)

    # SMTP 서버 연결 및 이메일 전송
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # 보안 연결
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, 이메일, msg.as_string())

        print(f"✅ 이메일 전송 완료: {이메일}, 제목: {subject}")

        

    except Exception as e:
        print(f"🚨 프로모션 이메일 전송 실패: {str(e)}")



def send_welcome_email(이메일, 이름, 아이디, 가입일):
    print(f"📢 {이름}님에게 환영 이메일을 보내는 중...")

    """회원가입 환영 이메일 자동 발송"""
    subject = "[현대자동차] 회원가입을 환영합니다! 🚗"
    
    # HTML 이메일 내용
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
        <table style="width: 100%; max-width: 800px; margin: auto; background: white; padding: 30px; 
                    border-radius: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.1);">
            
            <!-- 헤더 (현대 로고 + 환영 아이콘) -->
            <tr>
                <td style="padding: 10px; text-align: left;">
                    <a href="https://www.hyundai.com" target="_blank">
                        <img src="cid:hyundai_logo" alt="현대 로고" style="width: 120px;">
                    </a>
                </td>
                <td style="padding: 10px; text-align: right;">
                    <img src="cid:welcome_icon" alt="가입 환영" style="width: 200px; background: none; border: none;">
                </td>
            </tr>

            <!-- 본문 -->
            <tr>
                <td colspan="2" style="padding: 30px; text-align: center;">
                    <h2>
                        <span style="color: #005bac;">현대자동차 회원가입</span> 
                        <span style="color: #4B4B4B;">을 환영합니다!</span>
                    </h2>


                    <!-- 회원가입 안내 문구 왼쪽 정렬 -->
                    <div style="text-align: left; font-size: 18px; max-width: 600px; margin: auto;">
                        <p><strong>{이름}</strong> 고객님, 안녕하세요!</p>
                        <p>현대자동차의 회원이 되신 것을 진심으로 환영합니다.</p>
                        <p>앞으로 다양한 혜택과 맞춤형 프로모션 정보를 받아보실 수 있습니다.</p>
                    </div>
                    
                    <!-- 구분선 추가 -->
                    <div style="width: 100%; max-width: 600px; margin: 20px auto; border-bottom: 1px solid #ddd;"></div>


                    <!-- 회원 정보 테이블 -->
                    <table style="width: 100%; max-width: 500px; margin: auto; border-collapse: collapse; background: #f8f9fa; padding: 20px; border-radius: 10px; font-size: 16px; margin-top: 20px;">
                        <tr>
                            <td style="padding: 10px; font-weight: bold; text-align: left;">아이디</td>
                            <td style="padding: 10px; text-align: left;">{아이디}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold; text-align: left;">가입일</td>
                            <td style="padding: 10px; text-align: left;">{가입일}</td>
                        </tr>
                    </table>
                    
                    <a href="https://www.hyundai.com" 
                    style="display: inline-block; background: #005bac; color: white; padding: 15px 30px; 
                            text-decoration: none; border-radius: 8px; margin-top: 20px; font-size: 16px;">
                        현대자동차 구경하러가기
                    </a>
                </td>
            </tr>

            <!-- 푸터 -->
            <tr>
                <td colspan="2" style="padding: 15px; font-size: 14px; text-align: center; color: gray;">
                    ※ 본 메일은 자동 발송되었으며, 문의 사항은 고객센터를 이용해 주세요.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # 이메일 메시지 생성
    msg = MIMEMultipart()
    msg["From"] = "현대자동차"
    msg["To"] = 이메일
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    # 로고 이미지 첨부 (CID 참조)
    with open("main/project_1/img/hyundai_logo.jpg", "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<hyundai_logo>")
        msg.attach(img)

    # 웰컴 이미지 첨부 (CID 참조)
    with open("main/project_1/img/welcome.png", "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<welcome_icon>")
        msg.attach(img)

    # 이메일 전송
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, 이메일, msg.as_string())
        print(f"✅ 회원가입 환영 이메일 전송 완료: {이메일}")

    except Exception as e:
        print(f"🚨 환영 이메일 전송 실패: {str(e)}")



# **📌 이메일 전송 로그 파일 경로**
log_file_path = r"main\project_1\data_mini1\이메일_전송_로그.csv"

# **📌 자동 이메일 발송 스케줄링 기능 (중복 방지 + 반복문 종료)**
def send_scheduled_emails():
    print("📢 정기 이메일 발송 시작!")

    # 📌 CSV 파일이 존재하는지 확인
    if not os.path.exists(log_file_path):
        print("🚨 이메일 전송 로그 파일이 없습니다. 새로운 로그 파일을 생성합니다.")
        pd.DataFrame(columns=["이메일", "이름", "클러스터 ID", "전송 시간"]).to_csv(log_file_path, index=False)

    # 📌 이메일 전송 로그 불러오기
    customer_df = pd.read_csv(log_file_path)

    if customer_df.empty:
        print("✅ 이메일을 보낼 대상이 없습니다.")
        return

    # 📌 현재 시간 가져오기
    now = datetime.now()

    # 📌 5분 이상 경과한 고객만 필터링
    customer_df["전송 시간"] = pd.to_datetime(customer_df["전송 시간"], errors='coerce')
    eligible_customers = customer_df[customer_df["전송 시간"] + timedelta(minutes=5) <= now]

    if eligible_customers.empty:
        print("✅ 5분이 지나지 않아 보낼 고객이 없습니다.")
        return

    # 📌 이메일 전송
    for idx, row in eligible_customers.iterrows():
        send_promotion_email(row["이메일"], row["이름"], row["클러스터 ID"])
        time.sleep(5)  # 📌 5초 대기 (Gmail 차단 방지)

    
    print("✅ 모든 고객에게 이메일 전송 완료! 다음 실행까지 대기합니다.")


# **📌 스케줄 설정 (매일 오전 9시 실행)**
# schedule.every(5).minutes.do(send_scheduled_emails)

# 📌 스케줄 실행 함수
def schedule_worker():
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 확인
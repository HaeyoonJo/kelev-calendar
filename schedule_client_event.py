import datetime
import os.path
import pytz # 시간대 처리를 위한 라이브러리

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 이 스코프를 수정하는 경우 token.json 파일을 삭제하세요.
# 이 스코프는 이벤트를 생성하는 데 필요한 캘린더에 대한 전체 액세스를 허용합니다.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google_calendar():
    """
    구글 캘린더 API로 인증합니다.
    기존 token.json을 확인하고, 만료된 경우 새로 고치거나,
    토큰이 없는 경우 새 인증 흐름을 수행합니다.
    """
    creds = None
    # token.json 파일은 사용자 액세스 및 새로 고침 토큰을 저장하며,
    # 인증 흐름이 처음 완료될 때 자동으로 생성됩니다.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # 유효한 자격 증명이 없는 경우, 사용자에게 로그인하도록 합니다.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 이는 웹 기반 인증 흐름을 시작합니다.
            # 구글 계정에 로그인하고 앱에 권한을 부여하기 위한 브라우저 창이 열립니다.
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # 다음 실행을 위해 자격 증명을 저장합니다.
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def create_calendar_event(
    service,
    client_email,
    event_summary,
    event_description,
    start_datetime_str,
    end_datetime_str,
    timezone="Asia/Jerusalem" # 기본 시간대, 변경 가능합니다.
):
    """
    구글 캘린더 이벤트를 생성하고 보기 전용 액세스 권한으로 클라이언트를 초대합니다.
    인수:
        service: 구글 캘린더 API 서비스 객체.
        client_email (str): 초대할 클라이언트의 이메일 주소.
        event_summary (str): 이벤트의 제목.
        event_description (str): 이벤트에 대한 자세한 설명.
        start_datetime_str (str): "YYYY-MM-DD HH:MM" 형식의 시작 날짜 및 시간.
        end_datetime_str (str): "YYYY-MM-DD HH:MM" 형식의 종료 날짜 및 시간.
        timezone (str): 이벤트의 시간대 (예: "America/New_York", "Europe/London").
                        유효한 시간대는 다음에서 찾을 수 있습니다: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        reference: https://developers.google.com/workspace/calendar/api/v3/reference/events
    """
    try:
        # 날짜/시간 문자열을 구문 분석하고 지정된 시간대로 지역화합니다.
        local_tz = pytz.timezone(timezone)
        start_dt = local_tz.localize(datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M"))
        end_dt = local_tz.localize(datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M"))

        event = {
            'summary': event_summary,
            'description': event_description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': timezone,
            },
            'attendees': [
                {'email': client_email},
            ],
            # 클라이언트 권한에 대한 주요 설정:
            'guestsCanModify': False,      # 클라이언트는 이벤트를 수정할 수 없습니다.
            'guestsCanInviteOthers': False, # 클라이언트는 다른 사람을 초대할 수 없습니다.
            'guestsCanSeeOtherGuests': False, # 클라이언트는 다른 초대된 게스트를 볼 수 없습니다.
            'conferenceData': { # 선택 사항: 구글 Meet 링크를 추가하려면
                'createRequest': {
                    'requestId': f"meeting-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24시간 전
                    {'method': 'popup', 'minutes': 10},      # 10분 전
                ],
            },
        }

        # 기본 캘린더('primary')에 이벤트를 삽입합니다.
        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        print(f"이벤트가 생성되었습니다: {event.get('htmlLink')}")
        print(f"클라이언트 '{client_email}'가 성공적으로 초대되었습니다.")

    except HttpError as error:
        print(f"HTTP 오류가 발생했습니다: {error}")
        print("클라이언트 이메일이 유효하고 필요한 권한을 부여했는지 확인하세요.")
    except Exception as e:
        print(f"예기치 않은 오류가 발생했습니다: {e}")

def main():
    """
    일정 관리 애플리케이션을 실행하는 주요 함수입니다.
    """
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)

    print("\n--- 구글 캘린더 클라이언트 스케줄러 ---")
    print("이벤트 세부 정보를 입력하세요. 클라이언트 이메일에 'done'을 입력하여 종료합니다.")

    while True:
        client_email = input("\n클라이언트 이메일을 입력하세요 ('done'을 입력하여 종료): ").strip()
        if client_email.lower() == 'done':
            break

        event_summary = input("이벤트 요약을 입력하세요 (예: '[클라이언트 이름]과의 상담'): ").strip()
        event_description = input("이벤트 설명을 입력하세요 (예: '프로젝트 제안 논의'): ").strip()

        # 예시: 2025-07-31 10:00
        start_datetime_str = input("시작 날짜 및 시간을 입력하세요 (YYYY-MM-DD HH:MM, 예: 2025-08-15 14:00): ").strip()
        end_datetime_str = input("종료 날짜 및 시간을 입력하세요 (YYYY-MM-DD HH:MM, 예: 2025-08-15 15:00): ").strip()

        # 중요: 여기에 로컬 시간대를 설정하세요.
        # 유효한 시간대는 https://en.wikipedia.org/wiki/List_of_tz_database_time_zones 에서 찾을 수 있습니다.
        # 예시: "America/New_York", "Europe/London", "Asia/Tokyo", "Asia/Kolkata", "Asia/Jerusalem"
        event_timezone = input("이벤트 시간대를 입력하세요 (default: Asia/Jerusalem): ").strip()
        if not event_timezone:
            event_timezone = "Asia/Jerusalem" # 제공되지 않으면 예루살렘으로 기본 설정

        create_calendar_event(
            service,
            client_email,
            event_summary,
            event_description,
            start_datetime_str,
            end_datetime_str,
            event_timezone
        )

    print("\n일정 생성이 완료되었습니다. 종료합니다.")

if __name__ == "__main__":
    main()

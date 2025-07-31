import json, requests
from urllib.parse import urlencode
from django.contrib.auth import get_user_model
from django.utils import timezone
from social_token import get_valid_access_token
from config import settings

User = get_user_model()


def get_tokens_from_code(code: str, redirect_uri: str) -> dict:
    token_url = 'https://kauth.kakao.com/oauth/token'
    payload = {
        'grant_type': 'authorization_code',
        'client_id': settings.CLIENT_ID,
        'redirect_uri': redirect_uri,
        'code': code,
    }
    if settings.CLIENT_SECRET:
        payload['client_secret'] = settings.CLIENT_SECRET

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post(token_url, data=payload, headers=headers)
    result = response.json()

    if 'access_token' not in result:
        raise Exception(result.get('error_description', 'Failed to get access token'))
    return result

def get_kakao_user_info(access_token: str) -> dict:
    url = 'https://kapi.kakao.com/v2/user/me'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    result = response.json()
    return result


def save_or_update_user(user_info: dict, tokens: dict):
    kakao_id = str(user_info.get("id"))
    kakao_account = user_info.get("kakao_account", {})

    email = kakao_account.get("email")
    profile = kakao_account.get("profile", {})
    nickname = profile.get("nickname", "")
    profile_image = profile.get("profile_image_url")
    gender = kakao_account.get("gender")
    birthday_str = kakao_account.get("birthday")
    birthday_year = kakao_account.get("birthyear")
    has_talk_message = kakao_account.get("has_talk_message", False) 

    birthday = None
    if birthday_str and birthday_year:
        try:
            month = int(birthday_str[:2])
            day = int(birthday_str[2:])
            year = int(birthday_year)
            birthday = timezone.datetime(year, month, day).date()
        except (ValueError, TypeError):
            birthday = None

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")
    refresh_token_expires_in = tokens.get("refresh_token_expires_in")

    now = timezone.now()
    access_token_expire_at = now + timezone.timedelta(seconds=expires_in) if expires_in else None
    refresh_token_expire_at = now + timezone.timedelta(seconds=refresh_token_expires_in) if refresh_token_expires_in else None

    return User.objects.update_or_create(
        social_id=kakao_id,
        provider="KAKAO",
        defaults={
            "email": email,
            "nickname": nickname,
            "profile_image": profile_image,
            "gender": gender,
            "birthday": birthday,
            "has_talk_message": has_talk_message,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_token_expire_at": access_token_expire_at,
            "refresh_token_expire_at": refresh_token_expire_at,
            "updated_at": now,
        }
    )


def send_kakao_talk_message(user, message_text: str, link_url: str = None) -> dict:
    if not user.has_talk_message:
        raise Exception("메시지 보내기 권한이 없습니다.")
    access_token = get_valid_access_token(user)
    if not access_token:
        raise Exception("토큰이 만료되었거나 유효하지 않습니다. 재로그인이 필요합니다.")
    if not message_text or not isinstance(message_text, str):
        raise ValueError("메시지 텍스트가 유효하지 않습니다.")
    
    final_link = link_url or f"https://{settings.DOMAIN_NAME}"
    template_object = {
        "object_type": "text",
        "text": message_text,
        "link": {
            "web_url": final_link,
            "mobile_web_url": final_link,
        },
        "button_title": "확인하기" if link_url else "로그인 연장하기",
    }

    payload = {
        'template_object': json.dumps(template_object)
    }
    encoded_payload = urlencode(payload)

    url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post(url, data=encoded_payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"카카오톡 메시지 전송 실패: {response.text}")
    return response.json()
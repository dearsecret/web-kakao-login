import requests
from django.utils import timezone
from django.conf import settings

def refresh_access_token(user) -> str | None:
    """
    user의 refresh_token 으로 access_token 재발급 시도.
    성공 시 User 객체 업데이트 후 새 access_token 반환.
    실패 시 None 반환.
    """
    if not user.refresh_token or not user.is_refresh_token_valid():
        return None

    token_url = 'https://kauth.kakao.com/oauth/token'
    payload = {
        'grant_type': 'refresh_token',
        'client_id': settings.CLIENT_ID,
        'refresh_token': user.refresh_token,
    }
    if getattr(settings, "KAKAO_CLIENT_SECRET", None):
        payload['client_secret'] = settings.CLIENT_SECRET

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    resp = requests.post(token_url, data=payload, headers=headers)
    if resp.status_code != 200:
        return None

    result = resp.json()
    new_access_token = result.get('access_token')
    expires_in = result.get('expires_in')
    new_refresh_token = result.get('refresh_token')  # 가끔 새로 발급해주기도 함
    refresh_token_expires_in = result.get('refresh_token_expires_in')

    if not new_access_token or not expires_in:
        return None

    now = timezone.now()
    user.access_token = new_access_token
    user.access_token_expire_at = now + timezone.timedelta(seconds=expires_in)

    if new_refresh_token:
        user.refresh_token = new_refresh_token
        if refresh_token_expires_in:
            user.refresh_token_expire_at = now + timezone.timedelta(seconds=refresh_token_expires_in)

    user.save(update_fields=['access_token', 'access_token_expire_at', 'refresh_token', 'refresh_token_expire_at'])
    return new_access_token


def get_valid_access_token(user) -> str | None:
    """
    현재 저장된 access_token이 유효하면 반환,
    아니면 refresh_token 으로 갱신 시도 후 반환,
    실패 시 None 반환.
    """
    now = timezone.now()
    if user.access_token and user.access_token_expire_at and user.access_token_expire_at > now:
        return user.access_token
    return refresh_access_token(user)
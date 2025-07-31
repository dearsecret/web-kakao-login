from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.status import HTTP_200_OK
from users.models import User
from config.utils import decode_token, create_access_token , create_refresh_token
from datetime import timedelta, timezone
from .models import RefreshToken


def validate_refresh_token(refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise AuthenticationFailed("Refresh 토큰이 아닙니다.")
    user_id = payload.get("pk")
    token_id = payload.get("jti")
    try:
        token_obj = RefreshToken.objects.get(id=token_id, user_id=user_id)
    except RefreshToken.DoesNotExist:
        raise NotAuthenticated("서버에 저장된 Refresh 토큰이 없습니다.")
    now = timezone.now()
    if token_obj.expired_at < now:
        token_obj.delete()
        raise NotAuthenticated("Refresh 토큰이 만료되었습니다.")
    return payload


def refresh_tokens(payload: dict) -> dict:
    user_id = payload.get("pk")
    token_id = payload.get("jti")
    new_access_token = create_access_token(user_id)
    new_refresh_token, _ = create_refresh_token(user_id, token_id=token_id)
    token_obj = RefreshToken.objects.get(id=token_id, user_id=user_id)
    token_obj.expired_at = timezone.now() + timedelta(days=7)
    token_obj.save()
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }



def login_user_response(user, fcm_token=None, request=None):
    access_token = create_access_token(str(user.pk))
    refresh_token, token_id = create_refresh_token(str(user.pk))
    RefreshToken.objects.create(id=token_id, user=user, expired_at=timezone.now() + timedelta(days=7))
    if fcm_token:
        existing_user = User.objects.filter(fcm_token=fcm_token).exclude(pk=user.pk).first()
        if existing_user:
            # 필요시 푸시 강제 로그아웃 호출 주석 처리됨
            # send_force_logout_push(existing_user.fcm_token)
            existing_user.fcm_token = None
            existing_user.save()
        user.fcm_token = fcm_token
        user.save()
    return Response({"access_token": access_token,"refresh_token": refresh_token,},status=HTTP_200_OK,)
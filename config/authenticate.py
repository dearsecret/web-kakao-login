from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging
from .utils import validate_access_token

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTauthetication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token:
            token = request.COOKIES.get("access_token")
        if not token:
            return None
        try:
            payload = validate_access_token(token)
        except AuthenticationFailed as e:
            raise e 
        user_id = payload.get("pk")
        if not user_id:
            raise AuthenticationFailed("토큰에 사용자 정보가 없습니다.")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("사용자를 찾을 수 없습니다.")
        return (user, None)
        


from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RefreshToken
from .refresh_utils import validate_refresh_token, refresh_tokens
from common.cookies import set_auth_cookies, delete_auth_cookies

class WebAuth(APIView):

    def patch(self, request):
        refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh_token')
        if not refresh_token:
            response = Response({'detail': 'Refresh token이 없습니다.'}, status=401)
            return delete_auth_cookies(response)
        try:
            payload = validate_refresh_token(refresh_token)
            new_tokens = refresh_tokens(payload)
        except Exception:
            response = Response({'detail': '유효하지 않은 토큰입니다.'}, status=401)
            return delete_auth_cookies(response)
        response = Response({'success': True})
        return set_auth_cookies(response, request,new_tokens['access_token'], new_tokens['refresh_token'])


    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        RefreshToken.objects.filter(user=request.user).delete()
        logout(request)
        response = Response({'success': True, 'message': '로그아웃 완료'}, status=200)
        return delete_auth_cookies(response)

    



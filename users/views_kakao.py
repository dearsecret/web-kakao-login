from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RefreshToken
from common.cookies import set_auth_cookies ,set_csrf_cookie

from .social_kakao import get_tokens_from_code, get_kakao_user_info, save_or_update_user
from config.utils import create_state_token_with_cache,verify_state_token , create_access_token, create_refresh_token

User = get_user_model()

class KakaoAuthView(APIView):

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        redirect_uri = request.build_absolute_uri()
        if not code or not state:
            if not request.user.is_authenticated:
                from_url = request.GET.get('redirect')
                target_url = from_url if from_url else f"https://{settings.DOMAIN_NAME}"
                state = create_state_token_with_cache(target_url)
                # ↑ 로그인 완료 후 이동할 페이지 넣어줌 // 현재 프론트엔드 주소.
                kakao_auth_url = (
                    f"https://kauth.kakao.com/oauth/authorize"
                    f"?client_id={settings.KAKAO_CLIENT_ID}"
                    f"&redirect_uri={redirect_uri}"
                    f"&response_type=code"
                    f"&state={state}"
                    f"&scope=name,profile_image,profile_nickname,email,birthday,gender,talk_message"
                )
            else:
                kakao_auth_url = None
            return render(request, 'kakao/login_start.html', {
                'kakao_auth_url': kakao_auth_url,
                'is_logged_in': request.user.is_authenticated,
            })

        else:
            # code, state가 있는 경우 → 로그인 처리 페이지 렌더링
            # 해당 주소로 post 유도
            response = render(request, 'kakao/login_process.html', {
                'code': code,
                'state': state,
                'api_login_url': redirect_uri,
            })

            return set_csrf_cookie(response, request)



    def post(self, request):
        code = request.data.get('code')
        state = request.data.get('state')
        if not code or not state:
            return Response({'error': 'Missing code or state'}, status=400)
        try:
            from_url = verify_state_token(state)
            # 넣어준 url 복호화
            # kakao token : redirect_uri필요 
            if not from_url:
                return Response({'error': 'Invalid or expired state'}, status=400)
            redirect_uri = request.build_absolute_uri()
            tokens = get_tokens_from_code(code, redirect_uri)
            access_token = tokens['access_token']
            user_info = get_kakao_user_info(access_token)
            user, _ = save_or_update_user(user_info, tokens)

            # 항상 기존 토큰 제거
            RefreshToken.objects.filter(user=user).delete()
            jwt_access_token = create_access_token(str(user.id))
            jwt_refresh_token, token_id = create_refresh_token(str(user.id))
            RefreshToken.objects.create(
                id=token_id,
                user=user,
                expired_at=timezone.now() + timezone.timedelta(days=14)
            )

            response = Response({'success': True, 'redirect_url': from_url})
            return set_auth_cookies(response, request,jwt_access_token, jwt_refresh_token)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        

class KakaoWebhookView(APIView):
    authentication_classes = []  # 인증 없음
    permission_classes = []

    def post(self, request):
        data = request.data
        events = data.get("events", {})
        for event_type_url, event_data in events.items():
            subject = event_data.get("subject", {})
            kakao_id = subject.get("sub")
            if not kakao_id:
                continue
            try:
                user = User.objects.get(social_id=kakao_id, provider="KAKAO")
            except User.DoesNotExist:
                continue

            if event_type_url.endswith("tokens-revoked") or event_type_url.endswith("user-unlinked"):
                # is_active, deactivated_at 필드가 없다면 이 부분을 조정하세요.
                user.is_active = False  # 필요 시 모델에 필드 추가
                # user.deactivated_at = timezone.now()  # 모델에 필드 없으면 주석 처리
                user.save()

            elif event_type_url.endswith("user-scope-withdraw"):
                withdrawn_scopes = event_data.get("scope", [])
                # 필요 시 withdrawn_scopes 에 따라 추가 처리 가능

            elif event_type_url.endswith("user-scope-consent"):
                consented_scopes = event_data.get("scope", [])
                # 필요 시 consented_scopes 에 따라 추가 처리 가능

            elif event_type_url.endswith("user-linked"):
                # 앱 연결된 시점 - 필요 시 처리
                pass

            else:
                # 처리되지 않은 이벤트 타입
                pass

        return Response(status=200)


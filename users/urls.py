from django.urls import path
from . import views_kakao


urlpatterns = [
    path('kakao/state/', views_kakao.KakaoStateAPIView.as_view()),
    path('kakao/login/', views_kakao.KakaoLoginAPIView.as_view()),
    path('kakao/callback/', views_kakao.kakao_callback_view),
]
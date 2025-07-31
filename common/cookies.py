from django.conf import settings
from django.middleware.csrf import get_token

def set_csrf_cookie(response, request):
    csrf_token = get_token(request)
    response.set_cookie(
        key='csrftoken',
        value=csrf_token,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=60 * 60 * 24,  # 1일
        path='/',
        domain=f'.{settings.DOMAIN_NAME}',
        httponly=False
    )
    return response

def delete_auth_cookies(response):
    domain = f'.{settings.DOMAIN_NAME}'
    response.delete_cookie('access_token', path='/', domain=domain)
    response.delete_cookie('refresh_token', path='/', domain=domain)
    response.delete_cookie('csrftoken', path='/', domain=domain)
    return response


def set_auth_cookies(response, request, access_token, refresh_token):
    domain = f'.{settings.DOMAIN_NAME}'
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=60 * 30,
        path='/',
        domain=domain
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=60 * 60 * 24 * 14,
        path='/',
        domain=domain
    )
    return set_csrf_cookie(response, request)
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    PROVIDER_CHOICES = (
        ("KAKAO", "Kakao"),
        ("APPLE", "Apple"),
        ("GOOGLE", "Google"),
    )

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
    )

    social_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, blank=True, null=True)

    nickname = models.CharField(max_length=100, blank=True)
    profile_image = models.URLField(blank=True, null=True)

    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)

    fcm_token = models.CharField(max_length=512, blank=True, null=True)

    access_token = models.TextField(blank=True, null=True)
    access_token_expire_at = models.DateTimeField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    refresh_token_expire_at = models.DateTimeField(blank=True, null=True)
    has_talk_message = models.BooleanField(default=False, help_text="카카오톡 메시지 권한 동의 여부")

    @property
    def age(self):
        if not self.birthday:
            return None
        today = timezone.now().date()
        return today.year - self.birthday.year - (
            (today.month, today.day) < (self.birthday.month, self.birthday.day)
        )

    def __str__(self):
        return f"{self.provider}:{self.social_id or self.username}"
    

class RefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def __str__(self):
        return f"RefreshToken(user={self.user_id}, expired_at={self.expired_at})"
    
    @property
    def is_expired(self):
        return self.expired_at <= timezone.now()
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone


OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 10 * 60 

def generate_otp(n=OTP_LENGTH):
    return ''.join(secrets.choice('0123456789') for _ in range(n))

def make_otp_hash(otp: str, salt: str) -> str:
    return hashlib.sha256(f"{otp}{salt}".encode()).hexdigest()

def create_otp_for_user(user, purpose='email_verify', expiry_seconds=OTP_EXPIRY_SECONDS, otp_length=OTP_LENGTH):
    from .models import OTP
    otp = generate_otp(otp_length)
    salt = secrets.token_hex(16)
    otp_hash = make_otp_hash(otp, salt)
    expires_at = timezone.now() + timedelta(seconds=expiry_seconds)
    otp_obj = OTP.objects.create(user=user, otp_hash=otp_hash, salt=salt, purpose=purpose, expires_at=expires_at)
    return otp, otp_obj

def verify_otp_entry(otp_obj, candidate_otp: str) -> bool:
    if otp_obj.used:
        return False
    if otp_obj.is_expired():
        return False
    candidate_hash = make_otp_hash(candidate_otp, otp_obj.salt)
    return secrets.compare_digest(candidate_hash, otp_obj.otp_hash)

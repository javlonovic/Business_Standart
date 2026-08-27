"""
Property 2: Preservation - Existing Configuration Loading

These tests verify that existing working configurations continue to work
identically after the fix. They test JSON array format, other env vars, etc.

These tests should PASS on configurations that currently work.
"""
import pytest
import os
from app.core.config import Settings


def test_cors_origins_json_array_format():
    """Test that JSON array format CORS_ORIGINS still works"""
    # Set all required env vars
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost/test'
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
    os.environ['SECRET_KEY'] = 'test-secret-key-12345678'
    os.environ['S3_ENDPOINT_URL'] = 'https://s3.amazonaws.com'
    os.environ['S3_ACCESS_KEY'] = 'test-key'
    os.environ['S3_SECRET_KEY'] = 'test-secret'
    os.environ['S3_BUCKET_NAME'] = 'test-bucket'
    os.environ['PAYME_MERCHANT_ID'] = 'test-payme'
    os.environ['PAYME_SECRET_KEY'] = 'test-payme-secret'
    os.environ['CLICK_MERCHANT_ID'] = 'test-click'
    os.environ['CLICK_SECRET_KEY'] = 'test-click-secret'
    os.environ['SMS_GATEWAY_URL'] = 'https://api.example.com'
    os.environ['SMS_GATEWAY_TOKEN'] = 'test-token'
    os.environ['SMTP_HOST'] = 'smtp.example.com'
    os.environ['SMTP_USER'] = 'test@example.com'
    os.environ['SMTP_PASSWORD'] = 'test-password'
    os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    os.environ['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    
    # JSON array format (this might work on unfixed code in some environments)
    os.environ['CORS_ORIGINS'] = '["http://localhost:3000", "http://localhost:8080"]'
    
    # This should work and continue to work after fix
    settings = Settings()
    
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) == 2
    assert 'http://localhost:3000' in settings.CORS_ORIGINS
    assert 'http://localhost:8080' in settings.CORS_ORIGINS


def test_other_env_vars_unchanged():
    """Test that other environment variables load identically"""
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://custom:pass@dbhost:5432/mydb'
    os.environ['REDIS_URL'] = 'redis://redishost:6380/1'
    os.environ['SECRET_KEY'] = 'my-custom-secret-key-abcdefg'
    os.environ['ALGORITHM'] = 'HS512'
    os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '720'
    os.environ['CORS_ORIGINS'] = ''  # Empty to avoid parsing error
    os.environ['S3_ENDPOINT_URL'] = 'https://custom-s3.example.com'
    os.environ['S3_ACCESS_KEY'] = 'custom-access'
    os.environ['S3_SECRET_KEY'] = 'custom-secret'
    os.environ['S3_BUCKET_NAME'] = 'custom-bucket'
    os.environ['S3_REGION'] = 'eu-west-1'
    os.environ['PAYME_MERCHANT_ID'] = 'merchant-123'
    os.environ['PAYME_SECRET_KEY'] = 'payme-secret-456'
    os.environ['CLICK_MERCHANT_ID'] = 'click-789'
    os.environ['CLICK_SECRET_KEY'] = 'click-secret-abc'
    os.environ['SMS_GATEWAY_URL'] = 'https://sms.custom.com'
    os.environ['SMS_GATEWAY_TOKEN'] = 'sms-token-xyz'
    os.environ['SMTP_HOST'] = 'smtp.custom.com'
    os.environ['SMTP_PORT'] = '465'
    os.environ['SMTP_USER'] = 'custom@custom.com'
    os.environ['SMTP_PASSWORD'] = 'custom-smtp-pass'
    os.environ['CELERY_BROKER_URL'] = 'redis://redishost:6380/1'
    os.environ['CELERY_RESULT_BACKEND'] = 'redis://redishost:6380/1'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'WARNING'
    
    settings = Settings()
    
    # Verify all values are loaded correctly
    assert settings.DATABASE_URL == 'postgresql+asyncpg://custom:pass@dbhost:5432/mydb'
    assert settings.REDIS_URL == 'redis://redishost:6380/1'
    assert settings.SECRET_KEY == 'my-custom-secret-key-abcdefg'
    assert settings.ALGORITHM == 'HS512'
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 720
    assert settings.S3_ENDPOINT_URL == 'https://custom-s3.example.com'
    assert settings.S3_REGION == 'eu-west-1'
    assert settings.DEBUG is False
    assert settings.LOG_LEVEL == 'WARNING'


def test_empty_cors_origins_defaults_to_empty_list():
    """Test that empty CORS_ORIGINS defaults to empty list"""
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost/test'
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
    os.environ['SECRET_KEY'] = 'test-secret-key-12345678'
    os.environ['CORS_ORIGINS'] = ''
    os.environ['S3_ENDPOINT_URL'] = 'https://s3.amazonaws.com'
    os.environ['S3_ACCESS_KEY'] = 'test-key'
    os.environ['S3_SECRET_KEY'] = 'test-secret'
    os.environ['S3_BUCKET_NAME'] = 'test-bucket'
    os.environ['PAYME_MERCHANT_ID'] = 'test-payme'
    os.environ['PAYME_SECRET_KEY'] = 'test-payme-secret'
    os.environ['CLICK_MERCHANT_ID'] = 'test-click'
    os.environ['CLICK_SECRET_KEY'] = 'test-click-secret'
    os.environ['SMS_GATEWAY_URL'] = 'https://api.example.com'
    os.environ['SMS_GATEWAY_TOKEN'] = 'test-token'
    os.environ['SMTP_HOST'] = 'smtp.example.com'
    os.environ['SMTP_USER'] = 'test@example.com'
    os.environ['SMTP_PASSWORD'] = 'test-password'
    os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    os.environ['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    
    settings = Settings()
    
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Property 1: Fault Condition - Settings Instantiation with Comma-Separated CORS_ORIGINS

This test MUST FAIL on unfixed code - failure confirms the bug exists.

The test verifies that Settings successfully parses comma-separated CORS_ORIGINS
without raising json.decoder.JSONDecodeError during Docker container startup.
"""
import pytest
import os
from app.core.config import Settings


def test_cors_origins_comma_separated_single():
    """Test single origin in comma-separated format"""
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost/test'
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
    os.environ['SECRET_KEY'] = 'test-secret-key-12345678'
    os.environ['CORS_ORIGINS'] = 'http://localhost:3000'
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
    
    # This should NOT raise json.decoder.JSONDecodeError
    settings = Settings()
    
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == ['http://localhost:3000']


def test_cors_origins_comma_separated_multiple():
    """Test multiple origins in comma-separated format"""
    os.environ['CORS_ORIGINS'] = 'http://localhost:3000,http://localhost:8080,https://example.com'
    
    # This should NOT raise json.decoder.JSONDecodeError
    settings = Settings()
    
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) == 3
    assert 'http://localhost:3000' in settings.CORS_ORIGINS
    assert 'http://localhost:8080' in settings.CORS_ORIGINS
    assert 'https://example.com' in settings.CORS_ORIGINS


def test_cors_origins_with_whitespace():
    """Test comma-separated format with whitespace"""
    os.environ['CORS_ORIGINS'] = ' http://localhost:3000 , http://localhost:8080 '
    
    # This should NOT raise json.decoder.JSONDecodeError
    settings = Settings()
    
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) == 2
    # Whitespace should be stripped
    assert 'http://localhost:3000' in settings.CORS_ORIGINS
    assert 'http://localhost:8080' in settings.CORS_ORIGINS


def test_cors_origins_empty_string():
    """Test empty CORS_ORIGINS"""
    os.environ['CORS_ORIGINS'] = ''
    
    # This should NOT raise json.decoder.JSONDecodeError
    settings = Settings()
    
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

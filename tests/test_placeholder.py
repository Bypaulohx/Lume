
"""
Tests for Lume V2.0
"""

import pytest
from lume.utils import normalize_url, extract_params, build_url_with_params
from lume.utils.errors import LumeException, ValidationError
from lume.core import Config


class TestURLUtils:
    """Test URL utilities"""
    
    def test_normalize_url_adds_scheme(self):
        """Test that scheme is added if missing"""
        url = normalize_url("example.com")
        assert url.startswith("https://")
    
    def test_normalize_url_preserves_scheme(self):
        """Test that existing scheme is preserved"""
        url = normalize_url("http://example.com")
        assert url.startswith("http://")
    
    def test_extract_params_from_url(self):
        """Test parameter extraction"""
        url = "https://example.com/page?id=1&name=test"
        params = extract_params(url)
        assert "id" in params
        assert "name" in params
    
    def test_build_url_with_params(self):
        """Test building URL with parameters"""
        url = "https://example.com/page"
        test_url = build_url_with_params(url, {"id": "1", "test": "value"})
        assert "id=1" in test_url
        assert "test=value" in test_url


class TestConfig:
    """Test configuration loading"""
    
    def test_config_default_values(self):
        """Test that config has reasonable defaults"""
        config = Config()
        assert config.timeout > 0
        assert config.verify_tls is True
        assert config.max_workers > 0


class TestErrors:
    """Test custom exceptions"""
    
    def test_lume_exception_inheritance(self):
        """Test that custom exceptions inherit from LumeException"""
        from lume.utils.errors import ConnectionError, ScanError
        
        assert issubclass(ConnectionError, LumeException)
        assert issubclass(ScanError, LumeException)
    
    def test_exception_can_be_raised(self):
        """Test that exceptions can be raised"""
        with pytest.raises(LumeException):
            raise LumeException("Test error")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


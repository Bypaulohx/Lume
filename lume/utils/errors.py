"""
Custom exceptions for Lume V2.0
"""


class LumeException(Exception):
    """Base exception for Lume"""
    pass


class ConnectionError(LumeException):
    """Raised when connection to target fails"""
    pass


class TimeoutError(LumeException):
    """Raised when connection times out"""
    pass


class ScanError(LumeException):
    """Raised when scan operation fails"""
    pass


class ValidationError(LumeException):
    """Raised when input validation fails"""
    pass


class ConfigurationError(LumeException):
    """Raised when configuration is invalid"""
    pass


class NmapError(LumeException):
    """Raised when nmap scan fails"""
    pass


class PlaywrightError(LumeException):
    """Raised when Playwright operation fails"""
    pass


class SSLAnalysisError(LumeException):
    """Raised when SSL/TLS analysis fails"""
    pass


class WAFDetectionError(LumeException):
    """Raised when WAF detection fails"""
    pass


class ReportGenerationError(LumeException):
    """Raised when report generation fails"""
    pass

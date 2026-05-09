"""
Configuration management for Lume V2.0
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Config:
    """Lume configuration settings"""
    
    # Core Settings
    timeout: float = 10.0
    verify_tls: bool = True
    user_agent: str = "Lume/2.0 (+https://github.com/lume-security/lume)"
    
    # Reconnaissance Settings
    enable_nmap_scan: bool = True
    nmap_args: str = "-p 80,443,8080,8443 -sV --script vuln"
    enable_subdomain_enum: bool = True
    enable_dns_recon: bool = True
    
    # Browser Automation Settings
    enable_playwright: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    wait_for_load: int = 5000  # milliseconds
    
    # Security Testing Settings
    enable_owasp_zap: bool = False  # Requires ZAP installation
    zap_url: str = "http://localhost:8080"
    enable_fuzzing: bool = True
    fuzzing_depth: str = "aggressive"  # light, medium, aggressive
    
    # TLS/SSL Analysis Settings
    enable_ssl_analysis: bool = True
    min_tls_version: str = "1.2"
    
    # Reporting Settings
    report_format: str = "pdf"  # pdf, html, json, markdown
    report_dir: str = "lume/reports"
    include_remediation: bool = True
    
    # Performance Settings
    max_workers: int = 4
    enable_async: bool = True
    
    # Logging Settings
    log_level: str = "INFO"
    log_dir: str = "lume/logs"
    
    # WAF Detection
    enable_waf_detection: bool = True
    
    _instance: Optional['Config'] = field(default=None, init=False, repr=False)
    
    @classmethod
    def load(cls, config_file: Optional[str] = None) -> 'Config':
        """Load configuration from environment variables and optional config file"""
        load_dotenv()
        
        config = cls(
            timeout=float(os.getenv("LUME_TIMEOUT", "10.0")),
            verify_tls=os.getenv("LUME_VERIFY_TLS", "true").lower() == "true",
            enable_nmap_scan=os.getenv("LUME_NMAP", "true").lower() == "true",
            enable_playwright=os.getenv("LUME_PLAYWRIGHT", "true").lower() == "true",
            enable_owasp_zap=os.getenv("LUME_ZAP", "false").lower() == "true",
            enable_fuzzing=os.getenv("LUME_FUZZING", "true").lower() == "true",
            max_workers=int(os.getenv("LUME_WORKERS", "4")),
            log_level=os.getenv("LUME_LOG_LEVEL", "INFO"),
        )
        
        cls._instance = config
        return config
    
    @classmethod
    def get(cls) -> 'Config':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls.load()
        return cls._instance

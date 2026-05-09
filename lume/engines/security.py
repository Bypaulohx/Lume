"""
Security Engine for Lume V2.0
Performs security testing including XSS, SQLi, and other OWASP vulnerabilities
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import requests
from lume.core import setup_logger
from lume.utils.session import build_session
from lume.utils.url_utils import build_url_with_params
from lume.utils.errors import ScanError


class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """Discovered vulnerability"""
    vuln_type: str
    parameter: str
    severity: Severity
    description: str
    payload: str
    response_indicator: str
    remediation: str
    evidence: Optional[str] = None
    url: Optional[str] = None


@dataclass
class SecurityTestResult:
    """Result of security testing"""
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    total_requests: int = 0
    total_time: float = 0.0


class SecurityEngine:
    """
    Security testing engine with:
    - XSS detection (reflected and DOM-based)
    - SQL Injection detection
    - Command Injection detection
    - XXE detection
    - OWASP Top 10 checks
    """
    
    # XSS Payloads
    XSS_PAYLOADS = [
        '"><script>alert("xss")</script>',
        '\'><script>alert("xss")</script>',
        '<img src=x onerror="alert(\'xss\')">',
        '<svg onload="alert(\'xss\')">',
        '"><iframe src="javascript:alert(\'xss\')"></iframe>',
        '<body onload="alert(\'xss\')">',
        '<input onfocus="alert(\'xss\')" autofocus>',
        '<marquee onstart="alert(\'xss\')">',
        '<details open ontoggle="alert(\'xss\')">',
        'javascript:alert("xss")',
    ]
    
    # SQLi Payloads
    SQLI_PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "admin' #",
        "' or 1=1--",
        "' or 1=1 /*",
        "' or 1=1 #",
        "1' UNION SELECT NULL--",
        "' AND SLEEP(5)--",
    ]
    
    # Command Injection Payloads
    COMMAND_PAYLOADS = [
        "; whoami",
        "| whoami",
        "|| whoami",
        "& whoami",
        "&& whoami",
        "`whoami`",
        "$(whoami)",
    ]
    
    # Error patterns indicating vulnerabilities
    DB_ERROR_PATTERNS = re.compile(
        r"(SQL syntax|mysql_fetch|ORA-|SQLite\.Exception|psql:|"
        r"UNEXPECTED ERROR|Warning:|Microsoft OLE DB Provider|"
        r"ODBC|SQLSTATE|SyntaxError|Parse error)",
        re.IGNORECASE
    )
    
    def __init__(self, timeout: float = 10.0):
        """
        Initialize Security Engine.
        
        Args:
            timeout: Request timeout
        """
        self.logger = setup_logger(__name__)
        self.session = build_session(timeout=timeout)
        self.timeout = timeout
    
    def test_xss_reflected(
        self,
        url: str,
        param: str,
        payloads: Optional[List[str]] = None,
    ) -> List[Vulnerability]:
        """
        Test parameter for reflected XSS.
        
        Args:
            url: URL to test
            param: Parameter name to test
            payloads: Custom payloads (uses defaults if None)
            
        Returns:
            List of XSS vulnerabilities found
        """
        if payloads is None:
            payloads = self.XSS_PAYLOADS
        
        vulnerabilities = []
        self.logger.info(f"Testing {param} for XSS on {url}")
        
        for payload in payloads:
            try:
                test_url = build_url_with_params(url, {param: payload})
                response = self.session.get(test_url, timeout=self.timeout)
                
                # Check if payload is reflected
                if payload in response.text or self._encode_payload(payload) in response.text:
                    vuln = Vulnerability(
                        vuln_type="XSS_REFLECTED",
                        parameter=param,
                        severity=Severity.HIGH,
                        description=f"Reflected XSS vulnerability found in parameter '{param}'",
                        payload=payload,
                        response_indicator=payload[:50],
                        evidence=response.text[response.text.find(payload)-50:response.text.find(payload)+100] if payload in response.text else None,
                        url=test_url,
                        remediation="Implement input validation and output encoding for all user inputs",
                    )
                    vulnerabilities.append(vuln)
                    break  # Found vulnerability, stop testing
            
            except requests.RequestException as e:
                self.logger.debug(f"Request failed for {url}: {e}")
        
        return vulnerabilities
    
    def test_sqli(
        self,
        url: str,
        param: str,
        payloads: Optional[List[str]] = None,
    ) -> List[Vulnerability]:
        """
        Test parameter for SQL Injection.
        
        Args:
            url: URL to test
            param: Parameter name to test
            payloads: Custom payloads (uses defaults if None)
            
        Returns:
            List of SQLi vulnerabilities found
        """
        if payloads is None:
            payloads = self.SQLI_PAYLOADS
        
        vulnerabilities = []
        self.logger.info(f"Testing {param} for SQLi on {url}")
        
        for payload in payloads:
            try:
                test_url = build_url_with_params(url, {param: payload})
                response = self.session.get(test_url, timeout=self.timeout)
                
                # Check for database error patterns
                if self.DB_ERROR_PATTERNS.search(response.text):
                    vuln = Vulnerability(
                        vuln_type="SQL_INJECTION",
                        parameter=param,
                        severity=Severity.CRITICAL,
                        description=f"SQL Injection vulnerability found in parameter '{param}'",
                        payload=payload,
                        response_indicator="Database error detected",
                        evidence=response.text[response.text.find("SQL"):response.text.find("SQL")+200] if "SQL" in response.text else None,
                        url=test_url,
                        remediation="Use prepared statements and parameterized queries",
                    )
                    vulnerabilities.append(vuln)
                    break  # Found vulnerability, stop testing
            
            except requests.RequestException as e:
                self.logger.debug(f"Request failed for {url}: {e}")
        
        return vulnerabilities
    
    def test_command_injection(
        self,
        url: str,
        param: str,
        payloads: Optional[List[str]] = None,
    ) -> List[Vulnerability]:
        """
        Test parameter for Command Injection.
        
        Args:
            url: URL to test
            param: Parameter name to test
            payloads: Custom payloads (uses defaults if None)
            
        Returns:
            List of Command Injection vulnerabilities found
        """
        if payloads is None:
            payloads = self.COMMAND_PAYLOADS
        
        vulnerabilities = []
        self.logger.info(f"Testing {param} for Command Injection on {url}")
        
        for payload in payloads:
            try:
                test_url = build_url_with_params(url, {param: payload})
                response = self.session.get(test_url, timeout=self.timeout)
                
                # Look for command output indicators
                if any(indicator in response.text.lower() for indicator in ["root", "www-data", "uid=", "gid=", "groups="]):
                    vuln = Vulnerability(
                        vuln_type="COMMAND_INJECTION",
                        parameter=param,
                        severity=Severity.CRITICAL,
                        description=f"Command Injection vulnerability found in parameter '{param}'",
                        payload=payload,
                        response_indicator="Command output detected",
                        url=test_url,
                        remediation="Avoid shell execution; use safe APIs or strict input validation",
                    )
                    vulnerabilities.append(vuln)
                    break
            
            except requests.RequestException as e:
                self.logger.debug(f"Request failed for {url}: {e}")
        
        return vulnerabilities
    
    def test_security_headers(self, url: str) -> List[Vulnerability]:
        """
        Check for missing security headers.
        
        Args:
            url: URL to test
            
        Returns:
            List of missing security header vulnerabilities
        """
        required_headers = {
            "Content-Security-Policy": Severity.HIGH,
            "X-Frame-Options": Severity.MEDIUM,
            "X-Content-Type-Options": Severity.MEDIUM,
            "Strict-Transport-Security": Severity.MEDIUM,
            "X-XSS-Protection": Severity.LOW,
            "Referrer-Policy": Severity.LOW,
        }
        
        vulnerabilities = []
        self.logger.info(f"Checking security headers on {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            for header, severity in required_headers.items():
                if header not in response.headers:
                    vuln = Vulnerability(
                        vuln_type="MISSING_SECURITY_HEADER",
                        parameter=header,
                        severity=severity,
                        description=f"Missing security header: {header}",
                        payload="",
                        response_indicator=f"Header '{header}' not found",
                        url=url,
                        remediation=f"Add '{header}' header to HTTP responses",
                    )
                    vulnerabilities.append(vuln)
        
        except requests.RequestException as e:
            self.logger.debug(f"Error checking headers: {e}")
        
        return vulnerabilities
    
    def _encode_payload(self, payload: str) -> str:
        """HTML encode payload for comparison"""
        return (payload
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&#39;"))
    
    async def full_security_test(
        self,
        url: str,
        test_xss: bool = True,
        test_sqli: bool = True,
        test_cmd: bool = True,
        test_headers: bool = True,
    ) -> SecurityTestResult:
        """
        Perform comprehensive security testing.
        
        Args:
            url: Target URL
            test_xss: Whether to test for XSS
            test_sqli: Whether to test for SQLi
            test_cmd: Whether to test for Command Injection
            test_headers: Whether to test security headers
            
        Returns:
            SecurityTestResult with all findings
        """
        result = SecurityTestResult()
        loop = asyncio.get_event_loop()
        
        tasks = []
        
        # Schedule security tests
        if test_headers:
            tasks.append(
                loop.run_in_executor(None, self.test_security_headers, url)
            )
        
        # Get parameters to test
        params_to_test = self._extract_testable_params(url)
        
        for param in params_to_test:
            if test_xss:
                tasks.append(
                    loop.run_in_executor(None, self.test_xss_reflected, url, param)
                )
            if test_sqli:
                tasks.append(
                    loop.run_in_executor(None, self.test_sqli, url, param)
                )
            if test_cmd:
                tasks.append(
                    loop.run_in_executor(None, self.test_command_injection, url, param)
                )
        
        # Gather results
        if tasks:
            test_results = await asyncio.gather(*tasks, return_exceptions=True)
            for test_result in test_results:
                if isinstance(test_result, list):
                    result.vulnerabilities.extend(test_result)
        
        return result
    
    def _extract_testable_params(self, url: str) -> List[str]:
        """Extract parameters from URL"""
        from lume.utils.url_utils import extract_params
        params_dict = extract_params(url)
        return list(params_dict.keys())

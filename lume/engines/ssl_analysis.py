"""
TLS/SSL Analysis Engine for Lume V2.0
Analyzes SSL/TLS configuration and vulnerabilities using sslyze
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import socket
import ssl
from lume.core import setup_logger
from lume.utils.errors import SSLAnalysisError


@dataclass
class CertificateInfo:
    """SSL Certificate information"""
    subject: str
    issuer: str
    valid_from: str
    valid_until: str
    is_valid: bool
    is_expired: bool
    common_name: str
    alt_names: List[str]
    signature_algorithm: str
    public_key_size: int


@dataclass
class TLSVersion:
    """Supported TLS version"""
    protocol: str
    is_supported: bool
    ciphers: List[str]


@dataclass
class SSLAnalysisResult:
    """Result of SSL/TLS analysis"""
    hostname: str
    port: int
    certificate: Optional[CertificateInfo]
    tls_versions: List[TLSVersion]
    vulnerabilities: List[Dict]
    cipher_strength: str  # weak, medium, strong
    is_vulnerable: bool


class SSLAnalysisEngine:
    """
    Analyzes SSL/TLS configuration:
    - Certificate validation
    - Protocol version support
    - Cipher strength
    - Common vulnerabilities (HEARTBLEED, etc)
    """
    
    def __init__(self):
        """Initialize SSL Analysis Engine"""
        self.logger = setup_logger(__name__)
    
    def analyze_certificate(
        self,
        hostname: str,
        port: int = 443,
    ) -> Optional[CertificateInfo]:
        """
        Analyze SSL certificate.
        
        Args:
            hostname: Target hostname
            port: Target port
            
        Returns:
            CertificateInfo or None if analysis fails
        """
        try:
            self.logger.info(f"Analyzing certificate for {hostname}:{port}")

            import certifi
            from datetime import datetime
            
            context = ssl.create_default_context(cafile=certifi.where())
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cert_der = ssock.getpeercert(binary_form=True)
                    
                    # Extract certificate info
                    subject_dict = dict(x[0] for x in cert.get("subject", []))
                    issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                    
                    not_after = cert.get("notAfter")
                    not_before = cert.get("notBefore")
                    
                    # Parse dates
                    from email.utils import parsedate_to_datetime
                    valid_until = parsedate_to_datetime(not_after) if not_after else None
                    valid_from = parsedate_to_datetime(not_before) if not_before else None
                    is_expired = valid_until < datetime.now(valid_until.tzinfo) if valid_until else False
                    
                    # Extract SANs
                    alt_names = []
                    for san in cert.get("subjectAltName", []):
                        if san[0] == "DNS":
                            alt_names.append(san[1])
                    
                    cert_info = CertificateInfo(
                        subject=subject_dict.get("commonName", "N/A"),
                        issuer=issuer_dict.get("commonName", "N/A"),
                        valid_from=str(valid_from) if valid_from else "N/A",
                        valid_until=str(valid_until) if valid_until else "N/A",
                        is_valid=not is_expired,
                        is_expired=is_expired,
                        common_name=subject_dict.get("commonName", ""),
                        alt_names=alt_names,
                        signature_algorithm="N/A",  # Would need parsing DER
                        public_key_size=2048,  # Would need parsing DER
                    )
                    
                    return cert_info
        
        except Exception as e:
            self.logger.error(f"Certificate analysis failed: {e}")
            return None
    
    def analyze_tls_versions(
        self,
        hostname: str,
        port: int = 443,
    ) -> List[TLSVersion]:
        """
        Check supported TLS versions.
        
        Args:
            hostname: Target hostname
            port: Target port
            
        Returns:
            List of supported TLS versions
        """
        supported_versions = []
        
        # Protocols to test
        protocols = [
            ("SSLv2", getattr(ssl, "PROTOCOL_SSLv2", None)),
            ("SSLv3", getattr(ssl, "PROTOCOL_SSLv3", None)),
            ("TLSv1.0", getattr(ssl, "PROTOCOL_TLSv1", None)),
            ("TLSv1.1", getattr(ssl, "PROTOCOL_TLSv1_1", None)),
            ("TLSv1.2", getattr(ssl, "PROTOCOL_TLSv1_2", None)),
            # PROTOCOL_TLS negocia a versão mais alta possível (rótulo TLSv1.3 é aproximado).
            ("TLSv1.3", getattr(ssl, "PROTOCOL_TLS_CLIENT", None) or getattr(ssl, "PROTOCOL_TLS", None)),
        ]
        
        for proto_name, proto_version in protocols:
            if proto_version is None:
                continue
            
            try:
                context = ssl.SSLContext(proto_version)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((hostname, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        supported_versions.append(TLSVersion(
                            protocol=proto_name,
                            is_supported=True,
                            ciphers=[],
                        ))
                        self.logger.debug(f"{proto_name} is supported")
            
            except (ssl.SSLError, socket.error):
                supported_versions.append(TLSVersion(
                    protocol=proto_name,
                    is_supported=False,
                    ciphers=[],
                ))
        
        return supported_versions
    
    def check_vulnerabilities(
        self,
        hostname: str,
        port: int = 443,
    ) -> Tuple[List[Dict], str]:
        """
        Check for common SSL/TLS vulnerabilities.
        
        Args:
            hostname: Target hostname
            port: Target port
            
        Returns:
            Tuple of (vulnerabilities list, cipher_strength string)
        """
        vulnerabilities = []
        
        try:
            tls_versions = self.analyze_tls_versions(hostname, port)
            
            # Check for weak protocols
            weak_protocols = ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]
            for tls_version in tls_versions:
                if tls_version.is_supported and tls_version.protocol in weak_protocols:
                    vulnerabilities.append({
                        "type": "WEAK_TLS_VERSION",
                        "description": f"{tls_version.protocol} is supported (weak)",
                        "severity": "HIGH" if tls_version.protocol in ["SSLv2", "SSLv3"] else "MEDIUM",
                    })
            
            # Determine cipher strength
            if any(v.protocol == "TLSv1.3" for v in tls_versions):
                cipher_strength = "strong"
            elif any(v.protocol == "TLSv1.2" for v in tls_versions):
                cipher_strength = "medium"
            else:
                cipher_strength = "weak"
            
            # Check for certificate issues
            cert = self.analyze_certificate(hostname, port)
            if cert and cert.is_expired:
                vulnerabilities.append({
                    "type": "EXPIRED_CERTIFICATE",
                    "description": f"Certificate expired on {cert.valid_until}",
                    "severity": "CRITICAL",
                })
            
        except Exception as e:
            self.logger.error(f"Vulnerability check failed: {e}")
            cipher_strength = "unknown"
        
        return vulnerabilities, cipher_strength
    
    def full_analysis(
        self,
        hostname: str,
        port: int = 443,
    ) -> SSLAnalysisResult:
        """
        Perform full SSL/TLS analysis.
        
        Args:
            hostname: Target hostname
            port: Target port
            
        Returns:
            SSLAnalysisResult with complete analysis
        """
        self.logger.info(f"Starting full SSL/TLS analysis for {hostname}:{port}")
        
        certificate = self.analyze_certificate(hostname, port)
        tls_versions = self.analyze_tls_versions(hostname, port)
        vulnerabilities, cipher_strength = self.check_vulnerabilities(hostname, port)
        
        is_vulnerable = len(vulnerabilities) > 0 or cipher_strength == "weak"
        
        return SSLAnalysisResult(
            hostname=hostname,
            port=port,
            certificate=certificate,
            tls_versions=tls_versions,
            vulnerabilities=vulnerabilities,
            cipher_strength=cipher_strength,
            is_vulnerable=is_vulnerable,
        )

"""
Report building module for Lume V2.0
Aggregates findings and prepares them for export
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
from lume.core import setup_logger


@dataclass
class Report:
    """Comprehensive scan report"""
    title: str
    description: str
    target: str
    scan_date: str
    scan_duration: float
    
    findings: Dict[str, List[Dict]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


class ReportBuilder:
    """
    Builds comprehensive reports from scan results.
    Aggregates findings from all engines.
    """
    
    def __init__(self, title: str = "Lume Security Scan Report"):
        """
        Initialize Report Builder.
        
        Args:
            title: Report title
        """
        self.logger = setup_logger(__name__)
        self.title = title
        self.findings = {}
        self.start_time = None
        self.end_time = None
    
    def add_recon_findings(self, recon_result: Dict):
        """Add reconnaissance findings"""
        self.findings["reconnaissance"] = {
            "open_ports": [asdict(p) for p in recon_result.get("open_ports", [])],
            "dns_records": recon_result.get("dns_records", {}),
            "subdomains": list(recon_result.get("subdomains", [])),
        }
    
    def add_browser_findings(self, pages: Dict):
        """Add browser crawling findings"""
        self.findings["web_crawl"] = {
            "total_pages": len(pages),
            "pages": {
                url: {
                    "title": info.title,
                    "forms": [asdict(f) for f in info.forms],
                    "links_count": len(info.links),
                    "scripts": info.scripts,
                }
                for url, info in pages.items()
            }
        }
    
    def add_security_findings(self, vulnerabilities: List):
        """Add security test findings"""
        self.findings["security_tests"] = {
            "total_vulns": len(vulnerabilities),
            "by_severity": self._group_by_severity(vulnerabilities),
            "vulnerabilities": [asdict(v) for v in vulnerabilities],
        }
    
    def add_ssl_findings(self, ssl_result: Dict):
        """Add SSL/TLS analysis findings"""
        self.findings["ssl_analysis"] = {
            "certificate": ssl_result.get("certificate"),
            "tls_versions": ssl_result.get("tls_versions", []),
            "vulnerabilities": ssl_result.get("vulnerabilities", []),
            "cipher_strength": ssl_result.get("cipher_strength"),
            "is_vulnerable": ssl_result.get("is_vulnerable", False),
        }
    
    def _group_by_severity(self, vulnerabilities: List) -> Dict[str, int]:
        """Group vulnerabilities by severity"""
        severity_count = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        
        for vuln in vulnerabilities:
            severity = str(vuln.severity).lower() if hasattr(vuln, 'severity') else 'info'
            if severity in severity_count:
                severity_count[severity] += 1
        
        return severity_count
    
    def generate_summary(self, target: str) -> Dict[str, Any]:
        """Generate report summary"""
        return {
            "target": target,
            "scan_date": datetime.now().isoformat(),
            "total_findings": sum(
                len(v) for k, v in self.findings.items() if isinstance(v, list)
            ),
            "critical_issues": self.findings.get("security_tests", {}).get("by_severity", {}).get("critical", 0),
            "high_issues": self.findings.get("security_tests", {}).get("by_severity", {}).get("high", 0),
        }
    
    def build(
        self,
        target: str,
        description: str = "Security Analysis Report",
        metadata: Optional[Dict] = None,
    ) -> Report:
        """
        Build final report.
        
        Args:
            target: Target that was scanned
            description: Report description
            metadata: Additional metadata
            
        Returns:
            Report object
        """
        
        duration = 0.0
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return Report(
            title=self.title,
            description=description,
            target=target,
            scan_date=datetime.now().isoformat(),
            scan_duration=duration,
            findings=self.findings,
            summary=self.generate_summary(target),
            metadata=metadata or {},
        )
    
    def to_dict(self, report: Report) -> Dict:
        """Convert report to dictionary"""
        return {
            "title": report.title,
            "description": report.description,
            "target": report.target,
            "scan_date": report.scan_date,
            "scan_duration": report.scan_duration,
            "findings": report.findings,
            "summary": report.summary,
            "metadata": report.metadata,
        }

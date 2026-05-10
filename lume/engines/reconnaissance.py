"""
Reconnaissance Engine for Lume V2.0
Performs network scanning, port discovery, and DNS reconnaissance
"""

import nmap
import dns.resolver
import dns.rdatatype
import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from lume.core import setup_logger
from lume.utils.errors import NmapError


@dataclass
class PortInfo:
    """Information about discovered port"""
    port: int
    protocol: str
    state: str
    service: str
    version: Optional[str] = None


@dataclass
class DNSRecord:
    """DNS record information"""
    record_type: str
    value: str
    ttl: int


@dataclass
class ReconResult:
    """Result of reconnaissance scan"""
    target: str
    open_ports: List[PortInfo]
    dns_records: Dict[str, List[DNSRecord]]
    subdomains: Set[str]
    os_detection: Optional[str] = None


class ReconnaissanceEngine:
    """
    Performs reconnaissance tasks including:
    - Port scanning (nmap)
    - DNS record discovery
    - Subdomain enumeration
    """
    
    def __init__(self, timeout: int = 300):
        """
        Initialize Reconnaissance Engine.
        
        Args:
            timeout: Scan timeout in seconds
        """
        self.logger = setup_logger(__name__)
        self.timeout = timeout
        self._nm: Optional[nmap.PortScanner] = None
        self._nmap_available: Optional[bool] = None

    def _get_port_scanner(self) -> Optional[nmap.PortScanner]:
        """Cria PortScanner só quando necessário (evita erro se o binário nmap não existir)."""
        if self._nmap_available is False:
            return None
        if self._nm is not None:
            return self._nm
        try:
            self._nm = nmap.PortScanner()
            self._nmap_available = True
            return self._nm
        except nmap.PortScannerError as exc:
            self._nmap_available = False
            self.logger.warning(
                'Executável nmap não encontrado no PATH (%s). '
                'Instale o Nmap para Windows ou ignore o scan de portas.',
                exc,
            )
            return None
    
    def scan_ports(
        self,
        target: str,
        ports: str = "80,443,8080,8443",
        arguments: str = "-sV --script vuln",
    ) -> List[PortInfo]:
        """
        Scan target for open ports using nmap.
        
        Args:
            target: Target IP or hostname
            ports: Ports to scan (comma-separated)
            arguments: Additional nmap arguments
            
        Returns:
            List of PortInfo objects for open ports
            
        Raises:
            NmapError: If scan fails
        """
        try:
            nm = self._get_port_scanner()
            if nm is None:
                return []

            self.logger.info(f"Starting port scan on {target}")

            full_args = f"-p {ports} {arguments}"
            nm.scan(target, arguments=full_args, timeout=self.timeout)

            open_ports = []

            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports_dict = nm[host][proto]
                    
                    for port, port_info in ports_dict.items():
                        if port_info["state"] == "open":
                            port_obj = PortInfo(
                                port=port,
                                protocol=proto,
                                state=port_info["state"],
                                service=port_info.get("name", "unknown"),
                                version=port_info.get("version", None),
                            )
                            open_ports.append(port_obj)
            
            self.logger.info(f"Found {len(open_ports)} open ports")
            return open_ports
            
        except Exception as e:
            self.logger.error(f"Port scan failed: {e}")
            raise NmapError(f"Failed to scan ports on {target}: {e}")
    
    def discover_dns_records(
        self,
        domain: str,
        record_types: Optional[List[str]] = None,
    ) -> Dict[str, List[DNSRecord]]:
        """
        Discover DNS records for domain.
        
        Args:
            domain: Target domain
            record_types: Types of records to discover (A, MX, NS, TXT, etc.)
            
        Returns:
            Dictionary mapping record types to list of DNSRecord objects
        """
        if record_types is None:
            record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        
        records = {}
        self.logger.info(f"Discovering DNS records for {domain}")
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records[record_type] = [
                    DNSRecord(
                        record_type=record_type,
                        value=str(rdata),
                        ttl=answers.rrset.ttl,
                    )
                    for rdata in answers
                ]
                self.logger.debug(f"Found {len(records[record_type])} {record_type} records")
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
                records[record_type] = []
        
        return records
    
    def enumerate_subdomains(
        self,
        domain: str,
        wordlist: Optional[List[str]] = None,
    ) -> Set[str]:
        """
        Attempt to enumerate subdomains via DNS queries.
        
        Args:
            domain: Base domain
            wordlist: List of subdomain names to try (common names if None)
            
        Returns:
            Set of discovered subdomains
        """
        if wordlist is None:
            wordlist = [
                "www", "mail", "ftp", "localhost", "webmail",
                "smtp", "pop", "nameserver", "imap", "test",
                "admin", "api", "dev", "staging", "beta",
                "cdn", "static", "download", "upload", "vpn",
                "database", "db", "sql", "backup", "git",
                "jenkins", "monitoring", "metrics", "prometheus"
            ]
        
        subdomains = set()
        self.logger.info(f"Enumerating subdomains for {domain}")
        
        for subdomain in wordlist:
            full_domain = f"{subdomain}.{domain}"
            try:
                dns.resolver.resolve(full_domain, "A")
                subdomains.add(full_domain)
                self.logger.debug(f"Found subdomain: {full_domain}")
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
                pass
        
        self.logger.info(f"Discovered {len(subdomains)} subdomains")
        return subdomains
    
    async def full_recon(
        self,
        target: str,
        enable_port_scan: bool = True,
        enable_dns: bool = True,
        enable_subdomain: bool = True,
    ) -> ReconResult:
        """
        Perform full reconnaissance asynchronously.
        
        Args:
            target: Target hostname or IP
            enable_port_scan: Whether to perform port scanning
            enable_dns: Whether to discover DNS records
            enable_subdomain: Whether to enumerate subdomains
            
        Returns:
            ReconResult containing all discovery information
        """
        
        tasks = []
        open_ports = []
        dns_records = {}
        subdomains = set()
        
        # Schedule port scan
        if enable_port_scan:
            loop = asyncio.get_event_loop()
            tasks.append(
                loop.run_in_executor(None, self.scan_ports, target)
            )
        
        # Schedule DNS discovery
        if enable_dns:
            loop = asyncio.get_event_loop()
            from lume.utils.url_utils import extract_domain
            domain = extract_domain(target) or target
            tasks.append(
                loop.run_in_executor(None, self.discover_dns_records, domain)
            )
        
        # Schedule subdomain enumeration
        if enable_subdomain:
            loop = asyncio.get_event_loop()
            from lume.utils.url_utils import extract_domain
            domain = extract_domain(target) or target
            tasks.append(
                loop.run_in_executor(None, self.enumerate_subdomains, domain)
            )
        
        # Wait for all tasks to complete (ordem = port scan, DNS, subdomínios)
        if tasks:
            gathered = await asyncio.gather(*tasks, return_exceptions=True)
            idx = 0
            if enable_port_scan:
                r = gathered[idx]
                idx += 1
                if isinstance(r, Exception):
                    self.logger.error(f"Port scan failed: {r}")
                else:
                    open_ports = r
            if enable_dns:
                r = gathered[idx]
                idx += 1
                if isinstance(r, Exception):
                    self.logger.error(f"DNS discovery failed: {r}")
                else:
                    dns_records = r
            if enable_subdomain:
                r = gathered[idx]
                idx += 1
                if isinstance(r, Exception):
                    self.logger.error(f"Subdomain enumeration failed: {r}")
                else:
                    subdomains = r

        return ReconResult(
            target=target,
            open_ports=open_ports,
            dns_records=dns_records,
            subdomains=subdomains,
        )

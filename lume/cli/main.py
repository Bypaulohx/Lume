"""
CLI for Lume V2.0
Main command-line interface for security scanning
"""

import click
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from lume import __version__, setup_logger
from lume.core import Config
from lume.utils import build_session, normalize_url
from lume.utils.errors import LumeException
from lume.engines import ReconnaissanceEngine, BrowserEngine, SecurityEngine, SSLAnalysisEngine
from lume.reporting import ReportBuilder
from lume.reporting.formatters import HTMLFormatter, JSONFormatter, PDFFormatter


console = Console()


def print_banner():
    """Display Lume banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🔒 LUME v{version} - Security Analysis Tool        ║
    ║     Do latim: iluminar falhas escondidas                 ║
    ║                                                           ║
    ║     Advanced Web Vulnerability Scanner                   ║
    ║     Behavioral & Infrastructure Analysis                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """.format(version=__version__)
    
    console.print(banner, style="cyan")


@click.group()
@click.version_option(version=__version__, prog_name="Lume")
def cli():
    """Lume V2.0 - Advanced Security Analysis Framework"""
    pass


@cli.command()
@click.option(
    "-u", "--url",
    required=True,
    help="Target URL (e.g., https://example.com/page?id=1)",
    type=str
)
@click.option(
    "-o", "--output",
    default="lume/reports",
    help="Output directory for reports",
    type=str
)
@click.option(
    "-f", "--format",
    default="html",
    help="Report format (html, json, pdf)",
    type=click.Choice(["html", "json", "pdf"]),
)
@click.option(
    "--no-recon",
    is_flag=True,
    help="Skip reconnaissance phase"
)
@click.option(
    "--no-browser",
    is_flag=True,
    help="Skip browser crawling phase"
)
@click.option(
    "--no-security",
    is_flag=True,
    help="Skip security testing phase"
)
@click.option(
    "--no-ssl",
    is_flag=True,
    help="Skip SSL/TLS analysis phase"
)
@click.option(
    "--timeout",
    default=10.0,
    help="Request timeout in seconds",
    type=float
)
@click.option(
    "--max-pages",
    default=50,
    help="Maximum pages to crawl",
    type=int
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging"
)
def scan(
    url: str,
    output: str,
    format: str,
    no_recon: bool,
    no_browser: bool,
    no_security: bool,
    no_ssl: bool,
    timeout: float,
    max_pages: int,
    verbose: bool,
):
    """
    Execute comprehensive security scan on target URL
    """
    print_banner()
    
    # Setup
    try:
        url = normalize_url(url)
        console.print(f"[cyan]Target:[/cyan] {url}", style="bold")
        
        # Load configuration
        config = Config.load()
        config.timeout = timeout
        config.max_workers = 4
        
        # Setup logger
        log_level = "DEBUG" if verbose else "INFO"
        logger = setup_logger("lume", log_dir=output, level=log_level)
        
        # Create output directory
        Path(output).mkdir(parents=True, exist_ok=True)
        
        # Initialize report builder
        report_builder = ReportBuilder(title=f"Lume Security Scan - {url}")
        start_time = datetime.now()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            # Phase 1: Reconnaissance
            if not no_recon:
                task_recon = progress.add_task(
                    "[cyan]Phase 1/4:[/cyan] Reconnaissance...",
                    total=100
                )
                
                try:
                    recon_engine = ReconnaissanceEngine(timeout=int(timeout * 30))
                    
                    # Extract domain from URL
                    from lume.utils.url_utils import extract_domain
                    domain = extract_domain(url)
                    
                    if domain:
                        ports = recon_engine.scan_ports(domain, ports="80,443,8080,8443")
                        dns_records = recon_engine.discover_dns_records(domain)
                        subdomains = recon_engine.enumerate_subdomains(domain)
                        
                        recon_result = {
                            "open_ports": ports,
                            "dns_records": dns_records,
                            "subdomains": subdomains,
                        }
                        
                        report_builder.add_recon_findings(recon_result)
                        
                        console.print(
                            f"[green]✓[/green] Found {len(ports)} open ports, "
                            f"{len(subdomains)} subdomains",
                            style="green"
                        )
                    
                    progress.update(task_recon, completed=100)
                
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Reconnaissance failed: {e}", style="yellow")
                    progress.update(task_recon, completed=100)
            
            # Phase 2: Browser Crawling
            if not no_browser:
                task_browser = progress.add_task(
                    "[cyan]Phase 2/4:[/cyan] Browser Automation...",
                    total=100
                )
                
                try:
                    browser_engine = BrowserEngine(
                        browser_type="chromium",
                        headless=True,
                        timeout=int(timeout * 1000)
                    )
                    
                    # Run browser phase
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    pages = loop.run_until_complete(
                        browser_engine.crawl(url, max_pages=max_pages)
                    )
                    
                    report_builder.add_browser_findings(pages)
                    
                    console.print(
                        f"[green]✓[/green] Crawled {len(pages)} pages",
                        style="green"
                    )
                    
                    progress.update(task_browser, completed=100)
                    
                    loop.run_until_complete(browser_engine.close())
                    loop.close()
                
                except Exception as e:
                    console.print(
                        f"[yellow]⚠[/yellow] Browser crawling failed: {e}",
                        style="yellow"
                    )
                    progress.update(task_browser, completed=100)
            
            # Phase 3: Security Testing
            if not no_security:
                task_security = progress.add_task(
                    "[cyan]Phase 3/4:[/cyan] Security Testing...",
                    total=100
                )
                
                try:
                    security_engine = SecurityEngine(timeout=timeout)
                    
                    # Run security tests
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    test_result = loop.run_until_complete(
                        security_engine.full_security_test(
                            url,
                            test_xss=True,
                            test_sqli=True,
                            test_cmd=False,
                            test_headers=True,
                        )
                    )
                    
                    report_builder.add_security_findings(test_result.vulnerabilities)
                    
                    console.print(
                        f"[green]✓[/green] Found {len(test_result.vulnerabilities)} vulnerabilities",
                        style="green"
                    )
                    
                    progress.update(task_security, completed=100)
                    loop.close()
                
                except Exception as e:
                    console.print(
                        f"[yellow]⚠[/yellow] Security testing failed: {e}",
                        style="yellow"
                    )
                    progress.update(task_security, completed=100)
            
            # Phase 4: SSL/TLS Analysis
            if not no_ssl:
                task_ssl = progress.add_task(
                    "[cyan]Phase 4/4:[/cyan] SSL/TLS Analysis...",
                    total=100
                )
                
                try:
                    ssl_engine = SSLAnalysisEngine()
                    
                    from lume.utils.url_utils import extract_domain, extract_port
                    domain = extract_domain(url)
                    port = extract_port(url)
                    
                    if domain and port:
                        ssl_result = ssl_engine.full_analysis(domain, port)
                        
                        report_builder.add_ssl_findings({
                            "certificate": ssl_result.certificate,
                            "tls_versions": ssl_result.tls_versions,
                            "vulnerabilities": ssl_result.vulnerabilities,
                            "cipher_strength": ssl_result.cipher_strength,
                            "is_vulnerable": ssl_result.is_vulnerable,
                        })
                        
                        console.print(
                            f"[green]✓[/green] SSL/TLS Analysis complete "
                            f"(Cipher: {ssl_result.cipher_strength})",
                            style="green"
                        )
                    
                    progress.update(task_ssl, completed=100)
                
                except Exception as e:
                    console.print(
                        f"[yellow]⚠[/yellow] SSL/TLS analysis failed: {e}",
                        style="yellow"
                    )
                    progress.update(task_ssl, completed=100)
        
        # Generate report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        report = report_builder.build(
            target=url,
            description="Comprehensive security analysis report",
            metadata={
                "scan_duration": duration,
                "lume_version": __version__,
            }
        )
        
        # Export report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format in ["html", "pdf"]:
            html_formatter = HTMLFormatter()
            html_path = f"{output}/lume_report_{timestamp}.html"
            html_formatter.format(report, html_path)
            console.print(f"[green]✓[/green] HTML Report: {html_path}", style="green")
            
            if format == "pdf":
                pdf_formatter = PDFFormatter()
                pdf_path = f"{output}/lume_report_{timestamp}.pdf"
                try:
                    pdf_formatter.format(html_path, pdf_path)
                    console.print(f"[green]✓[/green] PDF Report: {pdf_path}", style="green")
                except:
                    console.print("[yellow]⚠ PDF generation requires wkhtmltopdf[/yellow]")
        
        if format == "json":
            json_formatter = JSONFormatter()
            json_path = f"{output}/lume_report_{timestamp}.json"
            json_formatter.format(report, json_path)
            console.print(f"[green]✓[/green] JSON Report: {json_path}", style="green")
        
        # Summary
        summary_table = Table(title="Scan Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")
        
        summary_table.add_row("Target", url)
        summary_table.add_row("Duration", f"{duration:.2f}s")
        summary_table.add_row("Total Findings", str(report.summary.get("total_findings", 0)))
        summary_table.add_row("Critical Issues", str(report.summary.get("critical_issues", 0)))
        summary_table.add_row("High Issues", str(report.summary.get("high_issues", 0)))
        
        console.print("\n")
        console.print(summary_table)
        
        console.print("\n[green]✓ Scan complete![/green]\n", style="bold green")
    
    except LumeException as e:
        console.print(f"[red]✗ Error:[/red] {e}", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}", style="bold red")
        sys.exit(1)


@cli.command()
def version():
    """Show Lume version"""
    console.print(f"Lume v{__version__}")


if __name__ == "__main__":
    cli()

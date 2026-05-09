"""
Report formatters for Lume V2.0
Exports reports in various formats (PDF, HTML, JSON)
"""

import json
import pdfkit
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from lume.core import setup_logger
from lume.reporting.report_builder import Report


class PDFFormatter:
    """Converts HTML reports to PDF"""
    
    def __init__(self, wkhtmltopdf_path: str = None):
        """
        Initialize PDF Formatter.
        
        Args:
            wkhtmltopdf_path: Path to wkhtmltopdf executable
        """
        self.logger = setup_logger(__name__)
        self.config = {
            'enable-local-file-access': None,
        } if wkhtmltopdf_path is None else {
            'wkhtmltopdf': wkhtmltopdf_path,
            'enable-local-file-access': None,
        }
    
    def format(self, html_content: str, output_path: str) -> str:
        """
        Convert HTML to PDF.
        
        Args:
            html_content: HTML content
            output_path: Output file path
            
        Returns:
            Path to generated PDF
        """
        try:
            self.logger.info(f"Generating PDF report: {output_path}")
            pdfkit.from_string(html_content, output_path, options=self.config)
            self.logger.info(f"PDF report generated successfully")
            return output_path
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            raise


class HTMLFormatter:
    """Formats reports as interactive HTML"""
    
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .summary-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        .findings {
            margin-top: 40px;
        }
        
        .findings h2 {
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .finding {
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            border-left: 4px solid #ff6b6b;
        }
        
        .finding.critical {
            border-left-color: #d32f2f;
            background: #ffebee;
        }
        
        .finding.high {
            border-left-color: #f57c00;
            background: #fff3e0;
        }
        
        .finding.medium {
            border-left-color: #fbc02d;
            background: #fffde7;
        }
        
        .finding.low {
            border-left-color: #388e3c;
            background: #f1f8e9;
        }
        
        .finding h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .severity-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
            margin-right: 10px;
        }
        
        .severity-badge.critical {
            background: #d32f2f;
        }
        
        .severity-badge.high {
            background: #f57c00;
        }
        
        .severity-badge.medium {
            background: #fbc02d;
            color: #333;
        }
        
        .severity-badge.low {
            background: #388e3c;
        }
        
        .remediation {
            background: white;
            padding: 15px;
            margin-top: 15px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }
        
        .remediation strong {
            color: #667eea;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Lume Security Report</h1>
            <p>{{ description }}</p>
        </div>
        
        <div class="content">
            <h2 style="color: #333; margin-bottom: 20px;">📊 Executive Summary</h2>
            <div class="summary">
                <div class="summary-card">
                    <h3>Target</h3>
                    <div class="value">{{ target }}</div>
                </div>
                <div class="summary-card">
                    <h3>Scan Date</h3>
                    <div class="value">{{ scan_date }}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Findings</h3>
                    <div class="value">{{ summary.total_findings }}</div>
                </div>
                <div class="summary-card">
                    <h3>Critical Issues</h3>
                    <div class="value" style="color: #d32f2f;">{{ summary.critical_issues }}</div>
                </div>
            </div>
            
            {% if findings.security_tests %}
            <div class="findings">
                <h2>🛡️ Security Test Findings</h2>
                {% for vuln in findings.security_tests.vulnerabilities %}
                <div class="finding {{ vuln.severity }}">
                    <h3>
                        <span class="severity-badge {{ vuln.severity }}">{{ vuln.severity|upper }}</span>
                        {{ vuln.vuln_type }}
                    </h3>
                    <p><strong>Parameter:</strong> {{ vuln.parameter }}</p>
                    <p><strong>Description:</strong> {{ vuln.description }}</p>
                    <p><strong>Payload:</strong> <code>{{ vuln.payload }}</code></p>
                    <div class="remediation">
                        <strong>💡 How to Fix:</strong><br>
                        {{ vuln.remediation }}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if findings.reconnaissance %}
            <div class="findings">
                <h2>🔍 Reconnaissance Results</h2>
                {% if findings.reconnaissance.open_ports %}
                <h3>Open Ports</h3>
                <div class="finding">
                    {% for port in findings.reconnaissance.open_ports %}
                    <p>{{ port.port }}/{{ port.protocol }} - {{ port.service }} ({{ port.state }})</p>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if findings.reconnaissance.subdomains %}
                <h3>Discovered Subdomains</h3>
                <div class="finding">
                    {% for subdomain in findings.reconnaissance.subdomains %}
                    <p>{{ subdomain }}</p>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endif %}
            
            {% if findings.ssl_analysis %}
            <div class="findings">
                <h2>🔐 SSL/TLS Analysis</h2>
                <div class="finding {{ 'critical' if findings.ssl_analysis.is_vulnerable else 'low' }}">
                    <p><strong>Cipher Strength:</strong> <span style="text-transform: uppercase;">{{ findings.ssl_analysis.cipher_strength }}</span></p>
                    {% if findings.ssl_analysis.vulnerabilities %}
                    <h3>Vulnerabilities</h3>
                    {% for vuln in findings.ssl_analysis.vulnerabilities %}
                    <p>• {{ vuln.type }}: {{ vuln.description }}</p>
                    {% endfor %}
                    {% endif %}
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Generated by <strong>Lume V2.0</strong> - Advanced Security Analysis Tool</p>
            <p>Do latim: iluminar falhas escondidas</p>
        </div>
    </div>
</body>
</html>
"""
    
    def format(self, report: Report, output_path: str) -> str:
        """
        Format report as HTML.
        
        Args:
            report: Report object
            output_path: Output file path
            
        Returns:
            Path to generated HTML
        """
        try:
            logger = setup_logger(__name__)
            logger.info(f"Generating HTML report: {output_path}")
            
            template = Template(self.HTML_TEMPLATE)
            
            html_content = template.render(
                title=report.title,
                description=report.description,
                target=report.target,
                scan_date=report.scan_date,
                summary=report.summary,
                findings=report.findings,
            )
            
            Path(output_path).write_text(html_content, encoding='utf-8')
            logger.info("HTML report generated successfully")
            
            return output_path
        
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            raise


class JSONFormatter:
    """Exports reports as JSON"""
    
    def format(self, report: Report, output_path: str) -> str:
        """
        Format report as JSON.
        
        Args:
            report: Report object
            output_path: Output file path
            
        Returns:
            Path to generated JSON
        """
        try:
            logger = setup_logger(__name__)
            logger.info(f"Generating JSON report: {output_path}")
            
            report_dict = {
                "title": report.title,
                "description": report.description,
                "target": report.target,
                "scan_date": report.scan_date,
                "scan_duration": report.scan_duration,
                "findings": report.findings,
                "summary": report.summary,
                "metadata": report.metadata,
            }
            
            Path(output_path).write_text(
                json.dumps(report_dict, indent=2, default=str),
                encoding='utf-8'
            )
            logger.info("JSON report generated successfully")
            
            return output_path
        
        except Exception as e:
            logger.error(f"JSON generation failed: {e}")
            raise

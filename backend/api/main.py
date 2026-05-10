import asyncio
import sys
from typing import Any, Dict, List, Optional

# Python na Microsoft Store + Playwright: SelectorEventLoop não suporta subprocessos.
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from lume.engines.browser import BrowserEngine
from lume.engines.reconnaissance import DNSRecord, ReconnaissanceEngine
from lume.engines.security import SecurityEngine
from lume.engines.ssl_analysis import SSLAnalysisEngine
from lume.utils.url_utils import normalize_url, extract_domain, extract_params

MSG_ANALYSIS_GENERIC = (
    'Estamos analisando o site; isso pode levar alguns segundos dependendo da complexidade. '
    'Se algo falhar, o site pode estar indisponível ou a bloquear pedidos automatizados.'
)


class ScanRequest(BaseModel):
    url: str
    xss: bool = True
    sqli: bool = True
    headers: bool = True
    infra: bool = True
    ssl_tls: bool = True
    dynamic: bool = True
    timeout: int = 10
    insecure: bool = False


class HeaderFinding(BaseModel):
    header: str
    hint: str


class ScanResult(BaseModel):
    """Resultado parcial; campos extra são preservados na resposta JSON."""

    model_config = ConfigDict(extra='allow')

    type: str
    target: str


class ScanResponse(BaseModel):
    success: bool
    target: str
    results: List[ScanResult]
    message: Optional[str] = None


def _serialize_dns(records: Dict[str, List[DNSRecord]]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for key, items in records.items():
        out[key] = [
            {'record_type': r.record_type, 'value': r.value, 'ttl': r.ttl}
            for r in items
        ]
    return out


app = FastAPI(
    title='Lume Backend',
    description='API de varredura dinâmica e de segurança para Lume V2.0',
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    msgs = []
    for err in exc.errors():
        loc = '.'.join(str(x) for x in err.get('loc', []) if x != 'body')
        msgs.append(f'{loc}: {err.get("msg", "inválido")}' if loc else err.get('msg', 'inválido'))
    return JSONResponse(
        status_code=422,
        content={'detail': 'Pedido inválido. ' + ('; '.join(msgs) if msgs else 'Verifique os dados enviados.')},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://127.0.0.1:5173',
        'http://localhost:5173',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/api/health')
async def health_check() -> Dict[str, str]:
    return {'status': 'ok', 'service': 'Lume Backend'}


@app.post('/api/scan', response_model=ScanResponse)
async def run_scan(request: ScanRequest) -> ScanResponse:
    try:
        target_url = normalize_url(request.url)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail='URL inválida. Use um formato como exemplo.com ou https://exemplo.com',
        )

    if not (
        request.dynamic
        or request.infra
        or request.ssl_tls
        or request.headers
        or request.xss
        or request.sqli
    ):
        raise HTTPException(
            status_code=400,
            detail='Selecione pelo menos um tipo de análise (segurança, infraestrutura, SSL ou navegador).',
        )

    results: List[ScanResult] = []
    warnings: List[str] = []
    security_result = None
    need_security = request.headers or request.xss or request.sqli

    if request.dynamic:
        browser = BrowserEngine(headless=True, timeout=request.timeout * 1000)
        try:
            crawl_results = await browser.crawl(target_url, max_pages=10, max_depth=2)
            results.append(
                ScanResult(
                    type='dynamic',
                    target=target_url,
                    crawled_pages=len(crawl_results),
                    forms_found=sum(len(page.forms) for page in crawl_results.values()),
                    links_found=sum(len(page.links) for page in crawl_results.values()),
                )
            )
        except Exception:
            warnings.append('Varredura dinâmica (navegador): não foi possível concluir.')
            results.append(
                ScanResult(
                    type='dynamic',
                    target=target_url,
                    crawled_pages=0,
                    forms_found=0,
                    links_found=0,
                    notes=[MSG_ANALYSIS_GENERIC],
                )
            )
        finally:
            await browser.close()

    port_results: List[Dict[str, Any]] = []
    dns_records: Dict[str, List[Dict[str, Any]]] = {}
    subdomains: List[str] = []

    if request.infra:
        try:
            recon = ReconnaissanceEngine(timeout=request.timeout * 10)
            recon_result = await recon.full_recon(target_url)
            port_results = [
                {
                    'port': p.port,
                    'protocol': p.protocol,
                    'state': p.state,
                    'service': p.service,
                    'version': p.version,
                }
                for p in recon_result.open_ports
            ]
            dns_records = _serialize_dns(recon_result.dns_records)
            subdomains = sorted(list(recon_result.subdomains))
            results.append(
                ScanResult(
                    type='ports',
                    target=target_url,
                    open_ports=port_results,
                    dns_records=dns_records,
                    subdomains=subdomains,
                )
            )
        except Exception:
            warnings.append('Infraestrutura (portas/DNS): não foi possível concluir.')
            results.append(
                ScanResult(
                    type='ports',
                    target=target_url,
                    open_ports=[],
                    dns_records={},
                    subdomains=[],
                    notes=[MSG_ANALYSIS_GENERIC],
                )
            )

    if request.ssl_tls:
        try:
            ssl_engine = SSLAnalysisEngine()
            ssl_host = extract_domain(target_url) or target_url
            ssl_result = ssl_engine.full_analysis(ssl_host)
            results.append(
                ScanResult(
                    type='ssl',
                    target=target_url,
                    certificate={
                        'subject': ssl_result.certificate.subject if ssl_result.certificate else None,
                        'issuer': ssl_result.certificate.issuer if ssl_result.certificate else None,
                        'valid_from': ssl_result.certificate.valid_from if ssl_result.certificate else None,
                        'valid_until': ssl_result.certificate.valid_until if ssl_result.certificate else None,
                        'is_valid': ssl_result.certificate.is_valid if ssl_result.certificate else False,
                        'is_expired': ssl_result.certificate.is_expired if ssl_result.certificate else False,
                        'common_name': ssl_result.certificate.common_name if ssl_result.certificate else '',
                        'alt_names': ssl_result.certificate.alt_names if ssl_result.certificate else [],
                        'signature_algorithm': ssl_result.certificate.signature_algorithm
                        if ssl_result.certificate
                        else '',
                        'public_key_size': ssl_result.certificate.public_key_size
                        if ssl_result.certificate
                        else 0,
                    },
                    tls_versions=[
                        {
                            'protocol': v.protocol,
                            'is_supported': v.is_supported,
                            'ciphers': v.ciphers,
                        }
                        for v in ssl_result.tls_versions
                    ],
                    vulnerabilities=ssl_result.vulnerabilities,
                    cipher_strength=ssl_result.cipher_strength,
                    is_vulnerable=ssl_result.is_vulnerable,
                )
            )
        except Exception:
            warnings.append('Certificado SSL/TLS: não foi possível concluir.')
            results.append(
                ScanResult(
                    type='ssl',
                    target=target_url,
                    certificate=None,
                    tls_versions=[],
                    vulnerabilities=[],
                    cipher_strength='desconhecida',
                    is_vulnerable=False,
                    notes=[MSG_ANALYSIS_GENERIC],
                )
            )

    if need_security:
        try:
            security = SecurityEngine(timeout=float(request.timeout))
            security.session.verify = not request.insecure
            security_result = await security.full_security_test(
                target_url,
                test_xss=request.xss,
                test_sqli=request.sqli,
                test_cmd=False,
                test_headers=request.headers,
            )
        except Exception:
            warnings.append('Testes HTTP (headers, XSS, SQLi): não foi possível concluir.')
            security_result = None

    if security_result is not None:
        vulnerabilities = security_result.vulnerabilities

        headers_missing = [
            HeaderFinding(header=v.parameter, hint=v.remediation)
            for v in vulnerabilities
            if v.vuln_type == 'MISSING_SECURITY_HEADER'
        ]

        xss_findings = [
            {
                'param': v.parameter,
                'payload': v.payload,
                'url': v.url or target_url,
                'evidence': v.evidence or v.description,
            }
            for v in vulnerabilities
            if v.vuln_type.startswith('XSS')
        ]

        sqli_findings = [
            {
                'param': v.parameter,
                'payload': v.payload,
                'url': v.url or target_url,
                'evidence': v.evidence or v.description,
            }
            for v in vulnerabilities
            if v.vuln_type == 'SQL_INJECTION'
        ]

        query_params = extract_params(target_url)
        param_count = len(query_params)

        if request.headers:
            results.append(
                ScanResult(
                    type='headers',
                    target=target_url,
                    ok=len(headers_missing) == 0,
                    missing=headers_missing,
                    headers_seen={},
                    notes=['Resultado gerado pelo motor de segurança Lume.'],
                )
            )

        if request.xss:
            results.append(
                ScanResult(
                    type='xss',
                    target=target_url,
                    tested=param_count,
                    vulnerable=len(xss_findings) > 0,
                    findings=xss_findings,
                )
            )

        if request.sqli:
            results.append(
                ScanResult(
                    type='sqli',
                    target=target_url,
                    tested=param_count,
                    vulnerable=len(sqli_findings) > 0,
                    findings=sqli_findings,
                )
            )

    security_failed = need_security and security_result is None
    success = not security_failed
    message = '; '.join(warnings) if warnings else None
    if security_failed and not message:
        message = MSG_ANALYSIS_GENERIC

    return ScanResponse(
        success=success,
        target=target_url,
        results=results,
        message=message,
    )

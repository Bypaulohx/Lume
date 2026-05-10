/** Resultado de varredura de headers */
export interface HeadersResult {
  type: 'headers'
  target: string
  ok: boolean
  missing: Array<{ header: string; hint: string }>
  headers_seen: Record<string, string>
  notes: string[]
}

/** Resultado de varredura XSS */
export interface XssResult {
  type: 'xss'
  target: string
  tested: number
  vulnerable: boolean
  findings: Array<{
    param: string
    payload: string
    url: string
    evidence: string
  }>
}

/** Resultado de varredura SQLi */
export interface SqliResult {
  type: 'sqli'
  target: string
  tested: number
  vulnerable: boolean
  findings: Array<{
    param: string
    payload: string
    url: string
    evidence: string
  }>
}

export interface DynamicResult {
  type: 'dynamic'
  target: string
  crawled_pages: number
  forms_found: number
  links_found: number
  notes?: string[]
}

export interface PortInfo {
  port: number
  protocol: string
  state: string
  service: string
  version?: string
}

export interface DnsRecord {
  record_type: string
  value: string
  ttl: number
}

export interface PortResult {
  type: 'ports'
  target: string
  open_ports: PortInfo[]
  dns_records: Record<string, DnsRecord[]>
  subdomains: string[]
  notes?: string[]
}

export interface SslCertificate {
  subject: string
  issuer: string
  valid_from: string
  valid_until: string
  is_valid: boolean
  is_expired: boolean
  common_name: string
  alt_names: string[]
  signature_algorithm: string
  public_key_size: number
}

export interface SslVersion {
  protocol: string
  is_supported: boolean
  ciphers: string[]
}

export interface SslResult {
  type: 'ssl'
  target: string
  certificate?: SslCertificate | null
  tls_versions: SslVersion[]
  vulnerabilities: Array<{ type: string; description: string; severity: string }>
  cipher_strength: string
  is_vulnerable: boolean
  notes?: string[]
}

export type ScanResult = HeadersResult | XssResult | SqliResult | DynamicResult | PortResult | SslResult

export interface ScanResponse {
  success: boolean
  target: string
  results: ScanResult[]
  /** Avisos quando alguma etapa falhou parcialmente */
  message?: string | null
}

export interface ScanRequest {
  url: string
  xss?: boolean
  sqli?: boolean
  headers?: boolean
  infra?: boolean
  ssl_tls?: boolean
  dynamic?: boolean
  timeout?: number
  insecure?: boolean
}

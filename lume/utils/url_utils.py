"""
URL utilities for Lume V2.0
Handles URL parsing, normalization, and parameter extraction
"""

from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl, parse_qs
from typing import Dict, List, Tuple, Optional
import re


def normalize_url(url: str) -> str:
    """
    Normalize a URL to a standard format.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL
    """
    
    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    parsed = urlparse(url)
    
    # Ensure scheme
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path.split("/")[0]
    path = parsed.path if parsed.netloc else "/" + "/".join(parsed.path.split("/")[1:])
    
    # Rebuild URL
    rebuilt = urlunparse((
        scheme,
        netloc,
        path or "/",
        "",
        parsed.query,
        ""
    ))
    
    return rebuilt


def extract_params(url: str) -> Dict[str, List[str]]:
    """
    Extract query parameters from URL.
    
    Args:
        url: URL to parse
        
    Returns:
        Dictionary of parameters with list values
    """
    parsed = urlparse(url)
    return parse_qs(parsed.query, keep_blank_values=True)


def extract_path_params(url: str) -> List[str]:
    """
    Extract path segments from URL.
    
    Args:
        url: URL to parse
        
    Returns:
        List of path segments
    """
    parsed = urlparse(url)
    return [p for p in parsed.path.split("/") if p]


def build_url_with_params(base_url: str, params: Dict[str, str]) -> str:
    """
    Build URL with query parameters.
    
    Args:
        base_url: Base URL
        params: Dictionary of parameters
        
    Returns:
        URL with encoded parameters
    """
    parsed = urlparse(base_url)
    
    # Merge existing parameters
    existing_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    existing_params.update(params)
    
    query_string = urlencode(existing_params, doseq=True)
    
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query_string,
        parsed.fragment
    ))


def is_valid_url(url: str) -> bool:
    """
    Validate if URL format is correct.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL to parse
        
    Returns:
        Domain name or None
    """
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc
        # Remove port if present
        domain = netloc.split(":")[0]
        return domain
    except:
        return None


def extract_port(url: str) -> Optional[int]:
    """
    Extract port from URL.
    
    Args:
        url: URL to parse
        
    Returns:
        Port number or None
    """
    try:
        parsed = urlparse(url)
        if ":" in parsed.netloc:
            return int(parsed.netloc.split(":")[1])
        # Return default ports
        return 443 if parsed.scheme == "https" else 80
    except:
        return None


def is_internal_link(base_url: str, link: str) -> bool:
    """
    Check if link is internal (same domain).
    
    Args:
        base_url: Base URL to compare against
        link: Link to check
        
    Returns:
        True if link is internal
    """
    base_domain = extract_domain(base_url)
    link_domain = extract_domain(link)
    return base_domain == link_domain if base_domain and link_domain else False

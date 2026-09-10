import ipaddress
from urllib.parse import urljoin, urlparse


class UnsafeUrlError(ValueError):
    pass


def validate_source_url(url: str, approved_domain: str) -> str:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme != "https":
        raise UnsafeUrlError("source URL must use HTTPS")
    if not hostname or parsed.username or parsed.password:
        raise UnsafeUrlError("source URL must have a public hostname without credentials")
    if hostname != approved_domain and not hostname.endswith(f".{approved_domain}"):
        raise UnsafeUrlError("URL hostname is outside the approved domain")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address and (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
    ):
        raise UnsafeUrlError("private or reserved address is not allowed")
    return url


def validate_redirect(base_url: str, location: str, approved_domain: str) -> str:
    target = urljoin(base_url, location)
    return validate_source_url(target, approved_domain)

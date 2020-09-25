import logging
import socket
import ssl


logs = logging.getLogger(__name__)


class SslTls:
    """
    Args:
        - host: Server Host. Str.
        - port: Server Port. Int.
        - timeout: Timeout. Int.
    """
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.verify_mode = ssl.CERT_REQUIRED
        self._ssl_context.check_hostname = True
        try:
            self._establish_connection()
        except Exception as conn_err:
            logs.error(f"Error Establish Connection with host: {host}")
            logs.error(f"Connection Error: {conn_err}")

    def _establish_connection(self) -> None:
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as __skt__:
                with self._ssl_context.wrap_socket(sock=__skt__, server_hostname=self.host) as skt:
                    logs.info(f"TLS version: {skt.version()}")
                    logs.info(f"Certificate: {skt.getpeercert()}")
        except Exception as conn_err:
            logs.error(f"Connection Error: {conn_err}")

    @property
    def get_ssl_context(self):
        return self._ssl_context

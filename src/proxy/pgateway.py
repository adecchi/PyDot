from os import environ as env
import asyncio
import logging
from security.ssl_tls import SslTls

logs = logging.getLogger(__name__)
MAX_PAYLOAD_LENGTH = int(env.get("MAX_PAYLOAD_LENGTH", "1024"))


class Gateway(object):
    """ Gateway Proxy

     Args:
         - host: Server host. Str.
         - port: Server Port. Int.
         - timeout: Server timeout. Int.
     """

    def __init__(self, host: str, port: int, timeout: int):
        self._establish_tls(host, port, timeout)

    def _establish_tls(self, host, port, timeout):
        cert = SslTls(host, port, timeout)
        self.host = host
        self.port = port
        self.timeout = timeout
        self._ssl_context = cert.get_ssl_context

    async def cache_dns_request(self, domain: str):
        ...

    async def request_upstream_server(self, data: bytes) -> None:
        """
        DNS-TLS provider

        Args:
            - data: Type=Bytes.
        Returns:
            - Upstream Response. Type=bytes.
        """
        try:
            reader, writer = await asyncio.open_connection(
                host=self.host, port=self.port, ssl=self._ssl_context
            )
            logs.info(f"Request upstream server: {data}")
            writer.write(data)
            result = await reader.read(self.get_max_payload_length)
            logs.info(
                f"Received response from upstream {self.host}:{self.port}: {result}"
            )
            writer.close()
            logs.info("Upstream. Connection was closed.")
            await writer.wait_closed()
            return result
        except Exception as rus_error:
            logs.error(f"Error {rus_error}")

    @property
    def get_max_payload_length(self):
        return MAX_PAYLOAD_LENGTH

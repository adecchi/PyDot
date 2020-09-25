import asyncio
import logging
from asyncio import (
    StreamReader,
    StreamWriter
)
from proxy.pgateway import Gateway

logs = logging.getLogger(__name__)


class ProxyTcpProtocol(Gateway):
    """ TCP Proxy

     Args:
         - host: Server host. Str.
         - port: Server Port. Int.
         - timeout: Server timeout. Int.
     """

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__(host, port, timeout)

    async def handle_dns_request(self, reader: StreamReader, writer: StreamWriter) -> None:
        """
        OnConnection Callback.

        Args:
            - Reader: <StreamRead>
            - Writer: <StreamWriter>

        Returns
            - None
        """

        try:
            request = await asyncio.wait_for(
                reader.read(self.get_max_payload_length), self.timeout
            )
            addr = writer.get_extra_info("peername")
            logs.info(f"New query from {addr[0]}:{addr[1]}", addr)
            logs.info(f"Query Request: {request}")
            result = await self.request_upstream_server(request)
            writer.write(result)
            await writer.drain()
            logs.info(f"Connection [{addr}] is closed now.")
            writer.close()
            return result
        except Exception as hdr_error:
            logs.error(f"Error {hdr_error}")

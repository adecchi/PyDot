import asyncio
import logging
import struct
from proxy.pgateway import Gateway

logs = logging.getLogger(__name__)


class ProxyUdpProtocol(Gateway):
    """ UDP Proxy

     Args:
         - host: Server host. Str.
         - port: Server Port. Int.
         - timeout: Server timeout. Int.
     """

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__(host, port, timeout)

    def connection_made(self, transport):
        self.transport = transport

    async def async_handle(self, data, addr):
        data = struct.pack(">H", len(data)) + data
        result = await self.request_upstream_server(data)
        self.transport.sendto(result[2:], addr)

    def datagram_received(self, data, addr):
        logs.info(f"New (UDP) request from {addr}")
        logs.debug(f"Request data: {data}")
        loop = asyncio.get_event_loop()
        logs.debug("Task to handle UDP Request")
        loop.create_task(self.async_handle(data, addr))

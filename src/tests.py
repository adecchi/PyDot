import unittest
import ssl
import asyncio
import asynctest
from proxy.pgateway import Gateway
from proxy.ptcp import ProxyTcpProtocol


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper


class ProxyTests(unittest.TestCase):

    def setUp(self) -> None:
        ...

    def tearDown(self) -> None:
        ...

    def test_establish_tls(self):
        gw = Gateway('one.one.one.one', 853, 30)
        cert = ssl.create_default_context()
        self.assertTrue(gw._ssl_context, cert)

    @async_test
    async def test_main(self):
        dot_client = ProxyTcpProtocol('one.one.one.one', 853, 30)
        server = await asyncio.start_server(
            dot_client.handle_dns_request,
            '0.0.0.0',
            8853
        )
        port = server.sockets[0].getsockname()[1]
        self.assertEqual(port, 8853)

    @async_test
    async def test_handle_dns_request(self):
        dot_client = ProxyTcpProtocol('one.one.one.one', 853, 30)
        reader, writer = self.create_mocks()
        server = await asyncio.start_server(
            dot_client.handle_dns_request(reader, writer),
            '0.0.0.0',
            8859
        )
        port = server.sockets[0].getsockname()[1]
        self.assertEqual(port, 8859)

    def create_mocks(self):
        reader = asynctest.mock.Mock(asyncio.StreamReader)
        writer = asynctest.mock.Mock(asyncio.StreamWriter)
        reader.read.return_value = b"MiddleOut"
        reader.readuntil.return_value = b"HTTP/1.1 200 OK\r\n..."
        return reader, writer


class SecurityTests(unittest.TestCase):

    def setUp(self) -> None:
        ...

    def tearDown(self) -> None:
        ...


class PyDotTests(unittest.TestCase):

    def setUp(self) -> None:
        ...

    def tearDown(self) -> None:
        ...

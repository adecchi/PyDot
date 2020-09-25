#!/usr/bin/env python3
import argparse
import os
import asyncio
import logging
import configparser
from proxy.ptcp import ProxyTcpProtocol
from proxy.pudp import ProxyUdpProtocol


FORMAT = "%(asctime)s %(name)-4s %(process)d %(levelname)-6s %(funcName)-8s %(message)s"
config = configparser.ConfigParser()
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("DNS_TLS_PROXY")
log_level = logging.DEBUG
logger.setLevel(log_level)
logger.debug("Starting 'DNS_TLS_PROXY' server")
try:
    config_path = os.path.join(os.path.dirname(__file__), 'settings', 'config.ini')
    config.read(config_path)
except Exception as ex:
    logger.error(f"Error starting server {ex}")

DEFAULT_UPSTREAM_SERVER = config['DEFAULT']['DEFAULT_UPSTREAM_SERVER']
DEFAULT_UPSTREAM_PORT = config['DEFAULT']['DEFAULT_UPSTREAM_PORT']
DEFAULT_TCP_PORT = config['DEFAULT']['DEFAULT_TCP_PORT']
DEFAULT_UDP_PORT = config['DEFAULT']['DEFAULT_UDP_PORT']


parser = argparse.ArgumentParser(description="DNS Proxy over TLS")
parser.add_argument(
    "--listen-ip", default="0.0.0.0", help="Listen IP to the server. Default: 0.0.0.0"
)
parser.add_argument(
    "--tcp-port",
    type=int,
    default=DEFAULT_TCP_PORT,
    help="TCP port to listen. Default: {}".format(DEFAULT_TCP_PORT),
)
parser.add_argument(
    "--udp-port",
    type=int,
    default=DEFAULT_UDP_PORT,
    help="UDP port to listen. Default: {}".format(DEFAULT_UDP_PORT),
)
parser.add_argument(
    "--upstream-server",
    default=DEFAULT_UPSTREAM_SERVER,
    help='Upstream Server. Default: "{}"'.format(DEFAULT_UPSTREAM_SERVER),
)
parser.add_argument(
    "--upstream-port",
    type=int,
    default=DEFAULT_UPSTREAM_PORT,
    help='Upstream port. Default: "{}"'.format(DEFAULT_UPSTREAM_PORT),
)
parser.add_argument("-d", "--debug", action="store_true", help="DEBUG log level")


async def main():
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    log_level = logging.DEBUG if args.debug else logging.INFO
    try:
        dot_client = ProxyTcpProtocol(args.upstream_server, args.upstream_port, 30)
        server = await asyncio.start_server(
            dot_client.handle_dns_request,
            args.listen_ip,
            args.tcp_port,
            loop=loop
        )
        logger.info(f"DNS/TLS proxy started. "
                    f"listening on (TCP) {args.listen_ip}:{args.tcp_port}")

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: ProxyUdpProtocol(args.upstream_server, args.upstream_port, 30),
            local_addr=(args.listen_ip, args.udp_port)
        )
        logger.info(f"DNS/TLS proxy started. "
                    f"listening on (UDP) {args.listen_ip}:{args.udp_port}")

        async with server:
            await server.serve_forever()
    except Exception as ex:
        logger.error(f"Error starting server {ex}")


asyncio.run(main())

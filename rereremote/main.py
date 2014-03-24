from __future__ import print_function
import logging
import argparse
import os
import sys
import netifaces
import tornado.ioloop
from tornado.log import access_log, app_log
from rereremote import control
from rereremote.application import application

if sys.version_info < (3,):
    ustr = unicode
else:
    ustr = str

parser = argparse.ArgumentParser(description=
        'A simple presentation remote controller server')
parser.add_argument('-a', '--address', type=str, default='0.0.0.0',
                    help='Listen address')
parser.add_argument('-p', '--port', type=int, default=1234,
                    help='Listen port')
parser.add_argument('-k', '--key', type=ustr,
                    help='Password used to protect the server')

def print_server_running(address, port):
    if address != "0.0.0.0":
        ips = [address]
    else:
        # Guess!
        ips = []
        ifaces = netifaces.interfaces()
        for iface in ifaces:
            addresses = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
            for addrinfo in addresses:
                ip = addrinfo['addr']
                # Skip localhost
                if ip == "127.0.0.1":
                    continue
                ips.append(ip)

        if len(ips) == 0:
            # Okay, if there are no other interfaces, show localhost
            ips = ['127.0.0.1']

    if len(ips) == 1:
        print("Server is accessible through the following address:\n")
        print("    http://%s:%d/\n" % (ips[0], port))
        print("Access that address on your phone's browser to run the remote " +
              "control interface.\n")
    else:
        print("Server is accessible through the following addresses:\n")
        for ip in ips:
            print("    http://%s:%d/\n" % (ip, port))
        print("Access one of those addresses on your phone's browser to run " +
              "the remote control interface. If one fails, try with the next." +
              "\n")

def main():
    args = parser.parse_args()

    if args.key is None:
        key = os.getenv('REREREMOTE_KEY')
    else:
        key = args.key

    if key is None:
        print("You need to provide a key, either using -k argument or "+
              "REREREMOTE_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    control.app_key = key
    access_log.setLevel(logging.INFO)
    application.listen(args.port, address=args.address)

    tornado.ioloop.IOLoop.instance().add_timeout(0, lambda:
            print_server_running(args.address, args.port))

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

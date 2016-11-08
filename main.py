#!/usr/bin/python

import parser
import requests
import sys
import time

def get_index():
    r = requests.get("https://nordvpn.com/servers/")
    if r.status_code == 200:
        sys.stderr.write("Received new index\n")
        with open("index.html", "wb") as f:
            f.write(r.content)

def get_best_server():
    get_index()
    servers = parser.parse(
        open("index.html").read(),
        ("Poland", "Germany", "Switzerland", "Czech Republic")
    )
    if len(servers) == 0:
        sys.stderr.write("Could not find any servers\n")
        sys.exit(0)
    servers.sort(key=lambda x:x.load)
    lowest_load = servers[0].load
    good_servers = [s for s in servers if s.load == lowest_load and s.feature['openvpn_udp']]
    if len(good_servers) == 1:
        best_servers = good_servers
        best_servers[0].probe_time = 0
    else:
        best_servers = []
        for server in good_servers:
            start_t = time.time()
            try:
                requests.get('http://%s/' % server.domain)
            except:
                continue
            end_t = time.time()
            server.probe_time = end_t - start_t
            sys.stderr.write("%s\t%s\t%s\n" % (server.domain, server.load, server.probe_time))
            best_servers.append(server)

        best_servers.sort(key=lambda x:x.probe_time)

    for server in best_servers:
        sys.stderr.write(server.domain, server.probe_time)

    return best_servers[0]

if __name__ == "__main__":
    server = get_best_server()
    print "sudo openvpn %s.udp1194.ovpn" % server.domain

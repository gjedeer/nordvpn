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

def get_best_servers(good_servers):
    best_servers = []
    for server in good_servers:
        start_t = time.time()
        try:
            requests.get('http://%s/' % server.domain, timeout=3)
        except:
            continue
        end_t = time.time()
        server.probe_time = end_t - start_t
        sys.stderr.write("%s\t%s\t%s\n" % (server.domain, server.load, server.probe_time))
        best_servers.append(server)

    best_servers.sort(key=lambda x:x.probe_time)

    return best_servers

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
    best_servers = get_best_servers(good_servers)
    if len(best_servers) == 0:
        good_servers = servers[:len(servers)/5]
        sys.stdout.write("Shortlist failed - falling back to %d lowest loaded servers\n" % len(good_servers))
        best_servers = get_best_servers(good_servers)

#    for server in best_servers:
#        sys.stderr.write("%s\t%s\n" % (server.domain, server.probe_time))

    return best_servers[0]

if __name__ == "__main__":
    server = get_best_server()
    #print server.__dict__
    print "sudo openvpn %s.udp1194.ovpn" % server.domain

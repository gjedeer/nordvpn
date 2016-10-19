#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import requests_cache
import time
import urllib

requests_cache.install_cache('nordvpn_cache', expire_after=3600)

class Server:
    domain = None
    load = None
    location = None
    group = None
    short = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if key.startswith('__'):
                raise ValueError(key)

        self.__dict__.update(kwargs)

    def __repr__(self):
        return "%s - %d%%" % (self.apple_short, self.load)

def get_url(group, country):
    url_template = "https://nordvpn.com/wp-admin/admin-ajax.php?group=%s&country=%s&action=getGroupRows"
    return url_template % (
        urllib.quote_plus(group),
        urllib.quote_plus(country),
    )

def parse(html, parsed_countries=[]):
    servers = []

    soup = BeautifulSoup(html, 'html.parser')
    # Get featured servers
    entries = soup.find_all(class_="tr-row")
    for entry in entries:
        country = entry.find(class_="country-name").string

    # Get groupped servers
    groups = soup.find_all("a", class_="load-servers")
    for group_el in groups:
        country = group_el['data-country']
        group = group_el['data-group']
        if parsed_countries and country not in parsed_countries:
            continue

        print group, country

        group_ajax_url = get_url(group, country)
        r = requests.get(group_ajax_url)
        servers_in_group = r.json()
        
        for server_dict in servers_in_group:
            server = Server(**server_dict)
            servers.append(server)

    return servers


if __name__ == "__main__":
    print parse(open("index.html").read(), ("Poland", "Germany"))

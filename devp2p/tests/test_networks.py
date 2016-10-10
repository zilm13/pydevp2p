import os
import pytest
from devp2p.discovery import AllowedNetworks, ipaddress


@pytest.mark.parametrize(
    ('whitelist', 'blacklist', 'match', 'nomatch'), [
        # default lists should not match 'private' networks
        ('DEFAULT', 'DEFAULT', '8.8.8.8,78.19.221.37', '127.0.0.1,10.0.10.89'),
        # we allow '0.0.0.0' although strictyl that should be considered private
        ('DEFAULT', 'DEFAULT', '0.0.0.0', ''),
        # whitelisting can add private network ranges
        ('10.0.10.0/24', 'DEFAULT', '8.8.8.8,78.19.221.37,10.0.10.89', '127.0.0.1'),
        # emtpy blacklist essentially turns blacklist off
        ('DEFAULT', '', '8.8.8.8,78.19.221.37,10.0.10.89,127.0.0.1', ''),
        ('10.0.10.0/24', '', '8.8.8.8,78.19.221.37,10.0.10.89,127.0.0.1', ''),
])
def test_from_environment(whitelist, blacklist, match, nomatch, monkeypatch):
    if not whitelist == 'DEFAULT':
        monkeypatch.setenv(AllowedNetworks.ENVIRONMENT_WHITELIST_KEY, whitelist)
    if not blacklist == 'DEFAULT':
        monkeypatch.setenv(AllowedNetworks.ENVIRONMENT_BLACKLIST_KEY, blacklist)

    allowed = AllowedNetworks.from_environment()

    environ = os.environ.get(AllowedNetworks.ENVIRONMENT_BLACKLIST_KEY, '')
    environ += '||'
    environ += os.environ.get(AllowedNetworks.ENVIRONMENT_WHITELIST_KEY, '')

    for addr in filter(lambda _: len(_), match.split(',')):
        assert ipaddress.IPv4Address(unicode(addr)) in allowed, (addr, environ)
    for addr in filter(lambda _: len(_), nomatch.split(',')):
        assert ipaddress.IPv4Address(unicode(addr)) not in allowed, (addr, environ)

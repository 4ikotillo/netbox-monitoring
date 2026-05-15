import requests
from django.core.cache import cache

from .base import (
    HostStatus,
    ModemStatus,
    HostStatusResult,
    ModemStatusResult,
)

CACHE_TTL = 60
AUTH_CACHE_TTL = 3600


class ZabbixBackend:
    """
    Клиент Zabbix API. Поддерживает Zabbix 5.x (login/password)
    и Zabbix 6.x+ (token).
    """

    def __init__(self, url, token=None, timeout=10, username=None, password=None):
        self.api_url = url.rstrip("/") + "/api_jsonrpc.php"
        self.token = token
        self.username = username
        self.password = password
        self.timeout = timeout
        self._id = 1
        self._auth = None

    # ===== Authentication =====

    def _get_auth(self):
        if self.token:
            return self.token
        if self._auth:
            return self._auth
        cache_key = f"nbmon:auth:{self.api_url}"
        cached = cache.get(cache_key)
        if cached:
            self._auth = cached
            return self._auth
        payload = {
            "jsonrpc": "2.0", "method": "user.login",
            "params": {"user": self.username, "password": self.password},
            "id": self._next_id(),
        }
        r = requests.post(self.api_url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"].get("data", str(data["error"])))
        self._auth = data["result"]
        cache.set(cache_key, self._auth, AUTH_CACHE_TTL)
        return self._auth

    def _next_id(self):
        self._id += 1
        return self._id

    def _call(self, method, params, with_auth=True):
        payload = {
            "jsonrpc": "2.0", "method": method,
            "params": params, "id": self._next_id(),
        }
        if with_auth:
            payload["auth"] = self._get_auth()
        r = requests.post(self.api_url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"].get("data", str(data["error"])))
        return data.get("result", {})

    # ===== Public methods =====

    def test_connection(self):
        try:
            version = self._call("apiinfo.version", {}, with_auth=False)
            self._get_auth()
            return True, f"Zabbix {version} (auth ok)"
        except Exception as e:
            return False, str(e)

    def get_host_status(self, ip):
        """ICMP-проверка хоста через Zabbix items icmpping/icmppingsec."""
        cache_key = f"nbmon:host:{ip}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        try:
            hosts = self._call("host.get", {
                "output": ["hostid", "host", "name"],
                "filter": {"ip": ip},
            })
            if not hosts:
                result = HostStatusResult(status=HostStatus.UNKNOWN)
                cache.set(cache_key, result, CACHE_TTL)
                return result

            hostid = hosts[0]["hostid"]

            # icmpping = 1 ok, 0 dead
            ping_items = self._call("item.get", {
                "output": ["lastvalue", "lastclock", "key_"],
                "hostids": hostid,
                "search": {"key_": "icmpping"},
            })
            status = HostStatus.UNKNOWN
            rtt = None
            lastclock = None
            for it in ping_items:
                key = it.get("key_", "")
                if key.startswith("icmpping[") or key == "icmpping":
                    status = HostStatus.REACHABLE if it.get("lastvalue") == "1" else HostStatus.UNREACHABLE
                    lastclock = it.get("lastclock")
                elif "icmppingsec" in key:
                    try:
                        rtt = float(it.get("lastvalue") or 0) * 1000  # сек → мс
                    except (ValueError, TypeError):
                        pass

            result = HostStatusResult(
                status=status, rtt_ms=rtt,
                last_check=lastclock, zabbix_host_id=hostid,
            )
        except Exception:
            result = HostStatusResult(status=HostStatus.UNKNOWN)
        cache.set(cache_key, result, CACHE_TTL)
        return result

    def get_modem_status(self, modem):
        """
        Статус модема — стратегия зависит от modem.lookup_strategy.
        Возвращает ModemStatusResult.
        """
        from ..models.monitoring import ModemLookupStrategy
        cache_key = f"nbmon:modem:{modem.pk}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            strat = modem.lookup_strategy
            if strat == ModemLookupStrategy.PUBLIC_IP:
                result = self._modem_by_public_ip(modem.lookup_value)
            elif strat == ModemLookupStrategy.HOST_NAME:
                result = self._modem_by_host_name(modem.lookup_value)
            elif strat == ModemLookupStrategy.ITEM_KEY:
                result = self._modem_by_item_key(modem.host, modem.lookup_value)
            else:
                result = ModemStatusResult(status=ModemStatus.UNKNOWN)
        except Exception:
            result = ModemStatusResult(status=ModemStatus.UNKNOWN)

        cache.set(cache_key, result, CACHE_TTL)
        return result

    # ===== Modem lookup strategies =====

    def _modem_by_public_ip(self, ip):
        if not ip:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        hosts = self._call("host.get", {
            "output": ["hostid"],
            "filter": {"ip": ip},
        })
        if not hosts:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        return self._read_inet_checker_item(hosts[0]["hostid"])

    def _modem_by_host_name(self, name):
        if not name:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        hosts = self._call("host.get", {
            "output": ["hostid"],
            "filter": {"host": name},
        })
        if not hosts:
            hosts = self._call("host.get", {
                "output": ["hostid"],
                "search": {"name": name},
            })
        if not hosts:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        return self._read_inet_checker_item(hosts[0]["hostid"])

    def _modem_by_item_key(self, host, item_key):
        """
        Когда модем — это item на хосте роутера.
        Нужен router IP (берём из device.primary_ip4) + ключ item.
        """
        if not item_key:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        device = host.device
        if not device.primary_ip4:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        router_ip = str(device.primary_ip4.address.ip)
        hosts = self._call("host.get", {
            "output": ["hostid"], "filter": {"ip": router_ip},
        })
        if not hosts:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        return self._read_inet_checker_item(hosts[0]["hostid"], key=item_key)

    def _read_inet_checker_item(self, hostid, key="inet.checker.status"):
        """Читает значение item Internet Checker'а — формат '60 200 ok'."""
        items = self._call("item.get", {
            "output": ["lastvalue", "lastclock"],
            "hostids": hostid,
            "search": {"key_": key},
            "limit": 1,
        })
        if not items:
            return ModemStatusResult(status=ModemStatus.UNKNOWN)
        value = items[0].get("lastvalue")
        lastclock = items[0].get("lastclock")
        latency, code = self._parse_value(value)
        return ModemStatusResult(
            status=self._parse_status(value),
            latency_ms=latency, http_code=code,
            last_check=lastclock,
        )

    @staticmethod
    def _parse_value(value):
        if not value:
            return None, None
        parts = value.strip().split()
        try:
            return (int(parts[0]) if len(parts) > 0 else None,
                    int(parts[1]) if len(parts) > 1 else None)
        except (ValueError, IndexError):
            return None, None

    @staticmethod
    def _parse_status(value):
        if not value:
            return ModemStatus.UNKNOWN
        v = value.strip().lower()
        if v.endswith("ok"):
            return ModemStatus.OK
        if v.endswith("whitelist"):
            return ModemStatus.WHITELIST
        if v.endswith("no_internet"):
            return ModemStatus.NO_INTERNET
        return ModemStatus.UNKNOWN

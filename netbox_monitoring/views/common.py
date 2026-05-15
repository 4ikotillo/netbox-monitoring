from django.conf import settings
from ..backends.zabbix import ZabbixBackend
from ..models.zabbix import ZabbixServer


def get_backend(server: ZabbixServer) -> ZabbixBackend:
    timeout = settings.PLUGINS_CONFIG.get(
        "netbox_monitoring", {}
    ).get("zabbix_timeout", 10)
    return ZabbixBackend(
        server.url,
        token=server.token or None,
        timeout=timeout,
        username=server.username or None,
        password=server.password or None,
    )


def get_default_backend():
    server = ZabbixServer.objects.filter(is_active=True).first()
    return get_backend(server) if server else None

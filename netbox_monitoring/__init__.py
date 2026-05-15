from netbox.plugins import PluginConfig


class NetBoxMonitoringConfig(PluginConfig):
    name = "netbox_monitoring"
    verbose_name = "NetBox Monitoring"
    description = "Hosts + modems monitoring dashboard via Zabbix"
    version = "0.2.0"
    author = "4ikotillo"
    base_url = "monitoring"
    min_version = "4.0.0"
    default_settings = {"zabbix_timeout": 10}

    def ready(self):
        super().ready()
        # Триггерим регистрацию детекторов
        from . import detectors  # noqa


config = NetBoxMonitoringConfig

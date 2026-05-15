# netbox-monitoring

NetBox plugin for monitoring network hosts and modems via Zabbix.

## Features
- Host ICMP monitoring via Zabbix
- Modem Internet Checker status (ok/whitelist/no_internet)
- Auto-detect modems by device type (Huawei/TP-Link/Sistematics)
- Custom groups across sites
- Diagnostic hints
- Zabbix 5.x and 6.x+

## Install
```bash
pip install -e /path/to/netbox-monitoring
```
`configuration.py`:
```python
PLUGINS = ['netbox_monitoring']
PLUGINS_CONFIG = {'netbox_monitoring': {'zabbix_timeout': 10}}
```
```bash
python manage.py migrate netbox_monitoring
systemctl restart netbox
```

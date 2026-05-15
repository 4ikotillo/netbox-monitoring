from netbox.plugins.navigation import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label="Monitoring",
    groups=(
        ("Overview", (
            PluginMenuItem(
                link="plugins:netbox_monitoring:dashboard",
                link_text="Dashboard",
            ),
            PluginMenuItem(
                link="plugins:netbox_monitoring:group_add",
                link_text="New Group",
            ),
            PluginMenuItem(
                link="plugins:netbox_monitoring:zabbix_servers",
                link_text="Zabbix Servers",
            ),
        )),
    ),
    icon_class="mdi mdi-monitor-dashboard",
)

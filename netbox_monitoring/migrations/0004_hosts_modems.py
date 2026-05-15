from django.db import migrations, models
import django.db.models.deletion


def migrate_devices_to_hosts(apps, schema_editor):
    """
    Старые MonitoredDevice → новые MonitoredHost.
    OneToOneField с тем же device — миграция через прямой SQL не нужна,
    делаем через ORM.
    """
    MonitoredDevice = apps.get_model("netbox_monitoring", "MonitoredDevice")
    MonitoredHost = apps.get_model("netbox_monitoring", "MonitoredHost")
    for md in MonitoredDevice.objects.all():
        MonitoredHost.objects.update_or_create(
            device=md.device,
            defaults={
                "enabled": md.enabled,
                "icmp_check_enabled": True,
                "zabbix_host_id": md.zabbix_host_id or "",
            },
        )


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_monitoring", "0003_monitoringgroup"),
        ("dcim", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MonitoredHost",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("enabled", models.BooleanField(default=True)),
                ("icmp_check_enabled", models.BooleanField(default=True)),
                ("zabbix_host_id", models.CharField(blank=True, max_length=64)),
                ("device", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="monitoring_host",
                    to="dcim.device",
                )),
            ],
            options={
                "ordering": ["device"],
                "verbose_name": "Monitored Host",
                "verbose_name_plural": "Monitored Hosts",
            },
        ),
        migrations.CreateModel(
            name="MonitoredModem",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("name", models.CharField(max_length=100)),
                ("enabled", models.BooleanField(default=True)),
                ("lookup_strategy", models.CharField(
                    max_length=20, default="public_ip",
                    choices=[
                        ("public_ip", "Публичный IP в Zabbix host"),
                        ("host_name", "Hostname в Zabbix"),
                        ("item_key", "Item на хосте роутера"),
                    ],
                )),
                ("lookup_value", models.CharField(blank=True, max_length=255)),
                ("host", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="modems",
                    to="netbox_monitoring.monitoredhost",
                )),
                ("interface", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="monitoring_modems",
                    to="dcim.interface",
                )),
            ],
            options={
                "ordering": ["host", "name"],
                "verbose_name": "Monitored Modem",
                "verbose_name_plural": "Monitored Modems",
            },
        ),
        migrations.RunPython(migrate_devices_to_hosts, reverse_noop),
        migrations.DeleteModel(name="MonitoredDevice"),
    ]

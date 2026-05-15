from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('dcim', '0001_initial'), ('extras', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='ZabbixServer',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('url', models.URLField()),
                ('token', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['name'], 'verbose_name': 'Zabbix Server'},
        ),
        migrations.CreateModel(
            name='MonitoredDevice',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('zabbix_host_id', models.CharField(blank=True, max_length=64)),
                ('enabled', models.BooleanField(default=True)),
                ('device', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='monitoring_config',
                    to='dcim.device',
                )),
                ('zabbix_server', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='monitored_devices',
                    to='netbox_monitoring.zabbixserver',
                )),
            ],
            options={'ordering': ['device'], 'verbose_name': 'Monitored Device'},
        ),
    ]

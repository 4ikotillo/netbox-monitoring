from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('netbox_monitoring', '0002_zabbixserver_credentials'), ('dcim', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='MonitoringGroup',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('devices', models.ManyToManyField(blank=True, related_name='monitoring_groups', to='dcim.device')),
            ],
            options={'ordering': ['name'], 'verbose_name': 'Monitoring Group'},
        ),
    ]

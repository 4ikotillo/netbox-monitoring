from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('netbox_monitoring', '0001_initial')]
    operations = [
        migrations.AddField(model_name='zabbixserver', name='username',
            field=models.CharField(max_length=100, blank=True, default='')),
        migrations.AddField(model_name='zabbixserver', name='password',
            field=models.CharField(max_length=255, blank=True, default='')),
    ]

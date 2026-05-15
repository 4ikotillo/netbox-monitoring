from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("", views.MonitoringDashboardView.as_view(), name="dashboard"),

    # Sites
    path("site/<slug:site_slug>/",
         views.SiteMonitoringView.as_view(), name="site_detail"),
    path("site/<slug:site_slug>/add-host/",
         views.SiteHostAddView.as_view(), name="site_host_add"),
    path("site/<slug:site_slug>/remove-host/<int:mh_pk>/",
         views.SiteHostRemoveView.as_view(), name="site_host_remove"),

    # Groups
    path("group/new/", views.GroupCreateView.as_view(), name="group_add"),
    path("group/<int:pk>/", views.GroupMonitoringView.as_view(), name="group_detail"),
    path("group/<int:pk>/edit/", views.GroupEditView.as_view(), name="group_edit"),
    path("group/<int:pk>/delete/", views.GroupDeleteView.as_view(), name="group_delete"),
    path("group/<int:pk>/add-host/",
         views.GroupHostAddView.as_view(), name="group_host_add"),
    path("group/<int:pk>/remove-host/<int:mh_pk>/",
         views.GroupHostRemoveView.as_view(), name="group_host_remove"),

    # Hosts
    path("host/<int:pk>/", views.HostDetailView.as_view(), name="host_detail"),
    path("host/<int:pk>/autodetect/",
         views.HostAutodetectView.as_view(), name="host_autodetect"),
    path("host/<int:pk>/toggle/",
         views.HostToggleView.as_view(), name="host_toggle"),

    # Modems
    path("host/<int:host_pk>/modem/new/",
         views.ModemCreateView.as_view(), name="modem_add"),
    path("modem/<int:pk>/edit/",
         views.ModemEditView.as_view(), name="modem_edit"),
    path("modem/<int:pk>/delete/",
         views.ModemDeleteView.as_view(), name="modem_delete"),

    # Zabbix
    path("zabbix/", views.ZabbixServerListView.as_view(), name="zabbix_servers"),
    path("zabbix/add/", views.ZabbixServerCreateView.as_view(), name="zabbix_server_add"),
    path("zabbix/<int:pk>/edit/",
         views.ZabbixServerEditView.as_view(), name="zabbix_server_edit"),
    path("zabbix/<int:pk>/delete/",
         views.ZabbixServerDeleteView.as_view(), name="zabbix_server_delete"),
    path("zabbix/<int:pk>/test/",
         views.ZabbixServerTestView.as_view(), name="zabbix_test"),
]

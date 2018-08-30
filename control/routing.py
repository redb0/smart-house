from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path('ws/device/statistics/<int:device_id>', consumers.StatisticConsumer)  # <int:device_id>
]

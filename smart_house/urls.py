"""smart_house URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from control import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='home'),
    path('home/', views.index_view, name='home'),

    path('docs/', views.docs_view, name='documentation'),
    path('add_device/', views.add_device, name='add_device'),

    path('device/settings/<int:device_id>', views.device_settings_view, name='settings'),
    path('device/statistics/<int:device_id>', views.device_statistics_view, name='statistics'),
    path('device/control/<int:device_id>', views.device_control_view, name='control'),

    # path('device/control/<int:device_id>/<str:mode>', views.device_control_view, name='control'),


    path('admin/condition', views.condition_db, name='condition'),

    path('init', views.init_device_http, name='init'),
    path('start', views.start_view, name='start'),
    # path('post', views.get_device_statistic, name='post')


    # path('test/', views.test, name='test'),
]

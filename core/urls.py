"""smi_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

from core.views import test_echo, test_radio, test_radiozenit, test_radiosvodoba,\
    test_echo_full, test_radio_full, test_radiozenit_full, test_radiosvodoba_full, text, test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('text', text),
    path('test', test),

    path('test_echo', test_echo),
    path('test_radio', test_radio),
    path('test_radiozenit', test_radiozenit),
    path('test_radiosvodoba', test_radiosvodoba),
    path('test_echo_full', test_echo_full),
    path('test_radio_full', test_radio_full),
    path('test_radiozenit_full', test_radiozenit_full),
    path('test_radiosvodoba_full', test_radiosvodoba_full),
]

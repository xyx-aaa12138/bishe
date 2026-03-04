"""job_monitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, path
from users.views import register, user_login, user_home, user_logout
from analysis.views import dashboard
from crawler.views import run

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register),
    path('login/', user_login),
    path('logout/', user_logout),
    path('my-home/', user_home),
    path('dashboard/', dashboard),
    path('run/', run),
    path('', include('analysis.urls')),
]
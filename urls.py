"""scrapify_prj URL Configuration

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
from django.urls import path, re_path
from scrapify_app import views as v

urlpatterns = [
    #Public
    path('public/hc', v.public_hc, name='public_hc'),

    re_path(r'^$', v.importer_asin_ht, name='asin_importer'),

    path('importer/asin/', v.importer_asin_ht, name='importer_asin_ht'),
    path('importer/data/', v.importer_data_ht, name='importer_data_ht'),

   

    path('api/importer/asin/', v.importer_asin, name='asin_importer_asin'),
    path('api/importer/data/', v.importer_data, name='asin_importer_data'),

    

    
]

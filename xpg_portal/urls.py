from django.contrib import admin
from django.urls import path
from xpg_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('gene/<str:gene_name>/', views.gene_detail, name='gene_detail'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),  # 👈 new line
    path("disease-overview/", views.disease_overview, name="disease_overview"),
]



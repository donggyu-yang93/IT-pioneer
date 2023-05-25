from django.urls import path
from . import views


urlpatterns = [
    path('about_me/', views.About_Me.as_view()),
    path('', views.Landing.as_view()),
    # path('',views.landing),
]
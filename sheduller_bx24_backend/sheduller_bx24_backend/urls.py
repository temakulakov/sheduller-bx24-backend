from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sheduller/', include('sheduller.urls')),  # Обратите внимание на правильное включение sheduller.urls
]
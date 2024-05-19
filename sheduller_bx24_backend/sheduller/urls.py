from django.urls import path

from . import views

urlpatterns = [
    path("elements/", views.get_elements, name="elements"),
    path("sections/", views.get_sections, name="sections"),
    path("report/day", views.report_day, name="report_day"),  # Новый маршрут для report_day
]
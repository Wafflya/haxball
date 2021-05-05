from django.urls import path

from .views import ReservationList, delete_entry

app_name = 'reservation'

urlpatterns = [
    path('', ReservationList.as_view(), name='host_reservation'),
    path('remove/<int:pk>', delete_entry, name='delete_entry'),
]
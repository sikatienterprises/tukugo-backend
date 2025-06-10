from django.urls import path
from .views import map_page,save_location,get_all_locations

urlpatterns = [
    # path('current/', get_or_update_user_location),
    path('location-map/', map_page, name='location-map'),
    path('save-location/', save_location, name='save-location'),
    # path('map/', show_map, name='map'),
    path('get-all/', get_all_locations, name='get_all_locations'),


]

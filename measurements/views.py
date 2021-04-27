from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo


# Create your views here.

def calculate_distance_view(request):
    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    ip = '185.244.214.247'
    country, city, lat, lon= get_geo(ip)
    # print('lcoation country', country)
    # print('location city', city)
    # print('location  lat, lon', lat, lon)

    location = geolocator.geocode(city)
    # print('###', location)

    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)


    if form.is_valid():
        instance = form.save(commit=False)
        destination_= form.cleaned_data.get("destination")
        destination = geolocator.geocode(destination_)
        # print(destination)
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)

        distance = round(geodesic(pointA, pointB).km, 2)

        instance.location = location
        instance.distance = distance
        instance.save()

    context = {
        'distance': obj,
        'form': form,
    }

    return render(request, 'measurements/main.html', context)
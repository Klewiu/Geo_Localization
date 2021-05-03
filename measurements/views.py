from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium


# Create your views here.

def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None

    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    ip_=get_ip_address(request)
    print(ip_)
    ip = '185.244.214.247'
    country, city, lat, lon = get_geo(ip)
    location = geolocator.geocode(city)

    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)

    # initial map folium
    m = folium.Map(width=1000, height=500, location=get_center_coordinates(l_lat, l_lon), zoom_start=6)

    # location marker
    folium.Marker([l_lat, l_lon], tooltip='cllick here for more', popup=city['city'],
                    icon=folium.Icon(color='green')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_=form.cleaned_data.get("destination")
        destination = geolocator.geocode(destination_)

        # destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)

        # distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # folium map modification
        m = folium.Map(width=1000, height=500, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
        # location marker
        folium.Marker([l_lat, l_lon], tooltip='cllick here for more', popup=city['city'],
                      icon=folium.Icon(color='green')).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='cllick here for more', popup=destination,
                      icon=folium.Icon(color='red', icon='plane')).add_to(m)
        instance.location = location
        instance.distance = distance
        instance.save()
        # line between location and destination
        line=folium.PolyLine(locations=[pointA,pointB], weight=3, color='blue')
        m.add_child(line)

    m = m._repr_html_()
    m = m[:90] + '40' + m[92:]


    context = {
        'distance': distance,
        'destination': destination,
        'form': form,
        'map': m,
    }

    return render(request, 'measurements/main.html', context)
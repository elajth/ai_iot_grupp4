import requests
import json

def get_forecast(lon, lat):
    """Hämtar väderprognos från SMHI:s API med koordinater."""
    
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

    # Skicka begäran till API:et
    try:
        response = requests.get(url)
        response.raise_for_status()  # Kasta ett undantag om statuskod inte är 200
        return response.json()  # Om allt gick bra, returnera JSON-data
    except requests.exceptions.RequestException as e:
        print(f"Fel vid hämtning av väderdata: {e}")
        return None


def find_place(place_name):
    """Omvandlar ett platsnamn till koordinater med hjälp av OpenStreetMap Nominatim API."""
    url = f"https://nominatim.openstreetmap.org/search?city={place_name}&format=json"
    
    # Ange din egen User-Agent (ersätt med din egen information)
    headers = {
        "User-Agent": "testingapp/1.0 (test@test.com)"
    }

    try:
        response = requests.get(url, headers = headers, timeout=5)  # Timeout för att undvika hängningar
        response.raise_for_status()  # Kasta fel vid dålig respons
        data = response.json()

        if not data:  # Om API:et returnerar en tom lista
            print("Inga resultat hittades för platsen.")
            return None, None

        first_result = data[0]  # Tar första träffen
        return float(first_result["lat"]), float(first_result["lon"])  # Rätt ordning!

    except requests.exceptions.RequestException as e:
        print(f"Fel vid anrop till API: {e}")
        return None, None
    except json.decoder.JSONDecodeError:
        print("Fel vid tolkning av JSON.")
        return None, None

place_name = "stockholm"
lat, lon = find_place(place_name)
lat = round(lat, 4)
lon = round(lon, 4)
forecast = get_forecast(lon, lat)

# Hämta senaste 'timeSeries' objektet
latest_time_series = forecast['timeSeries'][-1]

# Hitta de parametrar som heter 't' och 'ws'
t_value = None
ws_value = None

for param in latest_time_series['parameters']:
    if param['name'] == 't':
        t_value = param['values'][0]
    if param['name'] == 'ws':
        ws_value = param['values'][0]

# Skriv ut värdena för 't' och 'ws'
print(f'Plats: {place_name}')
print(f"Senaste temperatur: {t_value} °C")
print(f"Senaste vindstyrka: {ws_value} m/s")
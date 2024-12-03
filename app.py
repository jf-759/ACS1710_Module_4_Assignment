import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        # the city, and the units (metric or imperial).
        # See the documentation here: https://openweathermap.org/current

        'q': city,
        'units': units,
        'appid': API_KEY


    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    # pp.pprint(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.
    if result_json.get('cod') == 200:
        weather = result_json['weather'][0]
        main = result_json['main']
        wind = result_json['wind']
        sys = result_json['sys']
    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
        context = {
            'date': datetime.now(),
            'city': result_json['name'],
            'description': weather['description'].capitalize(),
            'temp': main['temp'],
            'humidity': main['humidity'],
            'wind_speed': wind['speed'],
            'sunrise': datetime.fromtimestamp(sys['sunrise']),
            'sunset': datetime.fromtimestamp(sys['sunset']),
            'units_letter': get_letter_for_units(units),
            'icon': weather['icon']
        }

    else:

        context = {
            'error': f"Could not retreive weather data for '{city}'. Please try again."
        }

    return render_template('results.html', **context)

def fetch_weather_data(city, units):
    '''
    Fetch weather data for a given city and units from the OpenWeatherMap API.
    '''
    params = {
        
        'q': city,
        'units': units,
        'appid': API_KEY

    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    if response.status_code != 200:
        return{'error': data.get('message', 'unknown error')}
    return data

@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units', 'metric')

    weather_data1 = fetch_weather_data(city1, units)
    weather_data2 = fetch_weather_data(city2, units)


    temp1 = weather_data1['main']['temp']
    temp2 = weather_data2['main']['temp']
    humidity1 = weather_data1['main']['humidity']
    humidity2 = weather_data2['main']['humidity']
    wind_speed1 = weather_data1['wind']['speed']
    wind_speed2 = weather_data2['wind']['speed']
    sunset1 = datetime.fromtimestamp(weather_data1['sys']['sunset'])
    sunset2 = datetime.fromtimestamp(weather_data2['sys']['sunset'])

    temp_diff = temp1 - temp2
    humidity_diff = humidity1 - humidity2
    wind_speed_diff = wind_speed1 - wind_speed2
    sunset_diff_hours = (sunset1 - sunset2).total_seconds() / 3600

    context = {

        'city1': city1,
        'city2': city2,
        'todays_date': datetime.now(),
        'units': get_letter_for_units(units),
        'temp_diff': temp_diff,
        'humidity_diff': humidity_diff,
        'wind_speed_diff': wind_speed_diff,
        'sunset_diff_hours': sunset_diff_hours,
        'city1_icon': weather_data1['weather'][0]['icon'],
        'city2_icon': weather_data2['weather'][0]['icon']

    }

    return render_template('comparison_results.html', **context)




if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)

import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

def fetch_weather(min_date, max_date):
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 37.8716,
        "longitude": -122.2728,
        "start_date": min_date,
        "end_date": max_date,
        "hourly": ["temperature_2m", "rain", "weather_code"],
        "timezone": "America/Los_Angeles"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation: {response.Elevation()} m asl")
    # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(2).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["weather_code"] = hourly_weather_code

    df = pd.DataFrame(data = hourly_data)

    df['date'] = df['date'].dt.tz_convert('America/Los_Angeles').dt.tz_localize(None)
    df["hour"] = df["date"].dt.hour
    
    # Create the merge key: a date at midnight
    df['key_date'] = df['date'].dt.normalize()

    df.rename(columns={'rain':'rain_mm'}, inplace=True)
    return df

# df = fetch_weather('2015-08-14','2017-03-18')
# print(df)

def clean_weather_data(df):

    weather_code_map = { # AI-generated
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: light",
        53: "Drizzle: moderate",
        55: "Drizzle: dense",
        56: "Freezing drizzle: light",
        57: "Freezing drizzle: dense",
        61: "Rain: slight",
        63: "Rain: moderate",
        65: "Rain: heavy",
        66: "Freezing rain: light",
        67: "Freezing rain: heavy",
        71: "Snow fall: slight",
        73: "Snow fall: moderate",
        75: "Snow fall: heavy",
        77: "Snow grains",
        80: "Rain showers: slight",
        81: "Rain showers: moderate",
        82: "Rain showers: violent",
        85: "Snow showers: slight",
        86: "Snow showers: heavy",
        95: "Thunderstorm: moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    codes, uniques = pd.factorize(df['weather_code'])
    df['encoded_weather_code'] = codes    

    # Textual description of weather conditions
    df["weather_type"] = df["weather_code"].map(weather_code_map)
    
    # Convert to local units
    df['temp_f'] = df['temperature_2m'] * 9/5 + 32  # Convert to Fahrenheit

    # Drop unnecessary columns
    df.drop(columns=["weather_code","temperature_2m"], inplace=True) 

    return df

# clean_weather_data(df)
# print(df)
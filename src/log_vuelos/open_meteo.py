import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import fastparquet



import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
from loguru import logger
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

def df_meteo_open(start_date, end_date, longitude, latitude):


	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
	params = {
		"latitude": latitude,
		"longitude": longitude,
		"hourly": ["temperature_2m", "dew_point_2m", "wind_speed_10m", "wind_direction_10m", "wind_speed_80m", "wind_direction_80m", "temperature_80m", "temperature_120m", "visibility", "cloud_cover", "surface_pressure", "precipitation"],
		"start_date": start_date,
		"end_date": end_date,
	}
	responses = openmeteo.weather_api(url, params=params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_dew_point_2m = hourly.Variables(1).ValuesAsNumpy()
	hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
	hourly_wind_direction_10m = hourly.Variables(3).ValuesAsNumpy()
	hourly_wind_speed_80m = hourly.Variables(4).ValuesAsNumpy()
	hourly_wind_direction_80m = hourly.Variables(5).ValuesAsNumpy()
	hourly_temperature_80m = hourly.Variables(6).ValuesAsNumpy()
	hourly_temperature_120m = hourly.Variables(7).ValuesAsNumpy()
	hourly_visibility = hourly.Variables(8).ValuesAsNumpy()
	hourly_cloud_cover = hourly.Variables(9).ValuesAsNumpy()
	hourly_surface_pressure = hourly.Variables(10).ValuesAsNumpy()
	hourly_precipitation = hourly.Variables(11).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["dew_point_2m"] = hourly_dew_point_2m
	hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
	hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
	hourly_data["wind_speed_80m"] = hourly_wind_speed_80m
	hourly_data["wind_direction_80m"] = hourly_wind_direction_80m
	hourly_data["temperature_80m"] = hourly_temperature_80m
	hourly_data["temperature_120m"] = hourly_temperature_120m
	hourly_data["visibility"] = hourly_visibility
	hourly_data["cloud_cover"] = hourly_cloud_cover
	hourly_data["surface_pressure"] = hourly_surface_pressure
	hourly_data["precipitation"] = hourly_precipitation

	hourly_dataframe = pd.DataFrame(data = hourly_data)
	logger.info("\nHourly data\n", hourly_dataframe)


	ruta_meteo = BASE_DIR / "archivos_salida"
	nombre_archivo = f'meteo_open_{start_date[0:10]}_{end_date[0:10]}.parquet'
	ruta_parquet_meteo = Path(ruta_meteo / nombre_archivo)

	hourly_dataframe.to_parquet(ruta_parquet_meteo, index=False)

	return  hourly_dataframe

lat = 40.820730
lon = -3.093183

#df_meteo_open('2024-01-01', '2026-02-20', lon, lat)

#mejora. Leer el archivo parquet sacar la fecha mayor y si falta algún periodo añadirlo, pero si no no hacer nada, que sea incremental.
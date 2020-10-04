import requests, json
import pandas as pd

def _get_weather(datetime_string="2020-10-04T00:10:00ZP0D:PT1H", coordinates_string="47.4245,9.3767+54.9,8.9"):	
	# credentials -> make private if time permits
	username = "dalhousie_lakshminarayangupta"
	password = "ZQOKzdeux6J95"
	# get the weather of a given location for a particular date
	response = requests.get(f"https://{username}:{password}@api.meteomatics.com/{datetime_string}/precip_10min:mm,relative_humidity_2m:p,wind_speed_100m:kmh,direct_rad:W/{coordinates_string}/json?model=mix")
	# unwrap the json response
	json_response = response.json()

	# initialize an empty weather dataframe to store the weather conditions for all coordinates on given date
	weather_df = pd.DataFrame(columns=["precipitation", "humidity", "wind_speed", "solar_radiation"])
	# build the weather df by parsing through the json response for:
	## precipitation
	weather_df["precipitation"] = [ each_coordinate["dates"][0]["value"] for each_coordinate in json_response["data"][0]["coordinates"] ]
	## solar radiation
	weather_df["solar_radiation"] = [ each_coordinate["dates"][0]["value"] for each_coordinate in json_response["data"][3]["coordinates"] ]
	## humidity
	weather_df["humidity"] = [ each_coordinate["dates"][0]["value"] for each_coordinate in json_response["data"][1]["coordinates"] ]
	## wind speed
	weather_df["wind_speed"] = [ each_coordinate["dates"][0]["value"] for each_coordinate in json_response["data"][2]["coordinates"] ]
	## unit conversion from km/hr to miles/hr
	weather_df["wind_speed"] = weather_df["wind_speed"].astype(float).apply(lambda x: x*0.621371)
	
	return weather_df
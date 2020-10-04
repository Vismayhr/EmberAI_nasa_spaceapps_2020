import numpy as np
import pandas as pd
from .weather import _get_weather

class WildfireFeatureBuilder:

	def __init__(self, date_obj, polygon_ids, polygon_coords, campsites, power_stations, power_lines):
		self.date_obj = date_obj
		self.polygon_ids = polygon_ids
		self.polygon_coords = polygon_coords
		self.polygon_lat_lon = [f"{each_coord[0]},{each_coord[1]}" for each_coord in polygon_coords]
		self.polygon_lat_lon = "+".join(self.polygon_lat_lon)
		self.campsites = campsites
		self.power_stations = power_stations
		self.power_lines = power_lines

	def get_weather(self):
		self.date_for_weather, self.date_for_doy = self.build_date_for_weather()
		self.weather_df = _get_weather(datetime_string=self.date_for_weather, coordinates_string=self.polygon_lat_lon)
		return self.weather_df

	def build_date_for_weather(self):
		date_for_weather = self.date_obj.strftime("%Y-%m-%dT00:00:00ZP0D:PT1H")
		date_for_doy = self.date_obj.strftime("%Y/%m/%d")
		return date_for_weather, date_for_doy

	def build_features(self):
		doy = pd.Period(self.date_for_doy).dayofyear
		doy = np.array([doy]*len(self.campsites))
		polygon_coords = np.array(self.polygon_coords).T
		weather_features = np.array(self.weather_df).T
		self._features = np.vstack([doy, self.polygon_ids, polygon_coords[0], polygon_coords[1], self.campsites, self.power_stations, self.power_lines, weather_features[0], weather_features[1], weather_features[2], weather_features[3]]).T

	@property	
	def features(self):
		return self._features
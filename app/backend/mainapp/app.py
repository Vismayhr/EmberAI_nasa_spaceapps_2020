from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import os, sys
import pandas as pd
import numpy as np
import pickle
from backend_functions.feature_builder import WildfireFeatureBuilder
from datetime import datetime

# Create global variables used throughout the life of the application
data = None
trained_model = None

app = Flask(__name__, static_url_path='')
CORS(app)

# Load the datasets before the very first user request and have it available during the entire lifespan of the application.
# Hence, time taken for file I/O is reduced as the csv files (i.e datasets) are only read once and not for every user request.
@app.before_first_request
def setup():
	print(f"Setting up the server....")
	global data
	data = pd.read_csv(os.path.join(os.getcwd(), "mainapp/data/polygons_data.csv"))
	data = data.sort_values(by="polygon_id")

	global polygon_ids
	global polygon_coords
	global campsites
	global power_stations
	global power_lines
	# get the 46 polygon coords upfront to calculate weather
	polygon_coords = [eval(i) for i in list(data["coordinate_sw"].copy())]
	polygon_ids = np.array(list(data["polygon_id"].copy()))
	campsites = np.array(list(data["campsites"].copy()))
	power_stations = np.array(list(data["power_stations"].copy()))
	power_lines = np.array(list(data["power_lines"].copy()))

	global transformed_data
	for column in ["coordinate_sw", "coordinate_se", "coordinate_nw", "coordinate_ne", "fire_causes"]:
		data[column] = data[column].apply(eval) 
	transformed_data = data.T.to_dict()

	global trained_model
	trained_model = pickle.load(open("mainapp/models/model.sav", 'rb'))
	print("Server setup complete. The server can handle user requests now...", flush=True)

@app.route('/init', methods=['GET'])
def init():
	sys.stdout.flush()
	return "init done"

@app.route('/')
def go_home():
	return redirect(url_for('home'))

@app.route('/predict-wildfires', methods=['POST', 'GET'])
def home(): 
	if request.method == 'POST':
		date = request.args['predict_date']
		date_obj = datetime.strptime(date, "%Y/%m/%d")
		print(f"POST request received for prediction. Date: {date_obj}", flush=True)
	else:
		date_obj = datetime.now()
		print(f"GET request received for prediction. Using default values: {date_obj}", flush=True)

	# send all relevant fields to WildfireFeatureBuilder class
	wfb = WildfireFeatureBuilder(date_obj, polygon_ids, polygon_coords, campsites, power_stations, power_lines)

	# get weather for all coordinates on given date
	wfb.get_weather()

	# feature engineering for model predictions
	wfb.build_features()

	# Make the predictions
	predictions = list(trained_model.predict(wfb.features))

	# append the predictions to the JSON
	for index, _ in enumerate(transformed_data.values()):
		transformed_data[index].update({"fire_risk": predictions[index]})

	return jsonify(date=date_obj.strftime("%Y/%m/%d"), data=transformed_data)

# Set host to 0.0.0.0 so that it is accessible from 'outside the container'
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8001)))
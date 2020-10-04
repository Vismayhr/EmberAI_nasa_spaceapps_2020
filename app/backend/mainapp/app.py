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

	global polygon_coords
	global campsites
	global power_stations
	global power_lines
	# get the 46 polygon coords upfront to calculate weather
	polygon_coords = [eval(i) for i in list(data["coordinate_sw"].copy())]
	campsites = np.array(list(data["campsites"].copy()))
	power_stations = np.array(list(data["power_stations"].copy()))
	power_lines = np.array(list(data["power_lines"].copy()))

	global trained_model
	trained_model = pickle.load(open("mainapp/models/model.sav", 'rb'))
	print("Server setup complete. The server can handle user requests now...", flush=True)


@app.route('/init', methods=['GET'])
def init():
	sys.stdout.flush()
	return "DONE"


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

@app.route('/')
def go_home():
	return redirect(url_for('home'))

@app.route('/predict-wildfires', methods=['POST', 'GET'])
def home(): 
	if request.method == 'POST':
		form_values = request.form.to_dict()
		date = form_values['predict_date']
		date_obj = datetime.strptime(date, "%Y/%m/%d")
		print(f"POST request received for prediction. Date: {date}", flush=True)
	else:
		date_obj = datetime.now()
		print(f"GET request received for prediction. Using default values: {date_obj}", flush=True)

	
	# send all relevant fields to WildfireFeatureBuilder class
	wfb = WildfireFeatureBuilder(date_obj, polygon_coords, campsites, power_stations, power_lines)

	# get weather for all coordinates on given date
	wfb.get_weather()

	# feature engineering for model predictions
	wfb.build_features()

	# Make the predictions
	predictions = trained_model.predict(wfb.features)

	return jsonify(data=len(predictions))

@app.route('/visualize-past-data', methods=['POST', 'GET'])
def visualise_past_data():
	# if request.method == 'POST':
	# 	form_values = request.form.to_dict()
	# 	year = form_values['past_year']
	# 	week = form_values['past_week']
	# 	print(f"POST request received for past data. year: {year} and week: {week}", flush=True)
	
	# year = float(year)
	# week = float(week)
	# response = data.query_for_past_date(year, week)
	# return render_template('past_visualisation.html', data=response)
	pass

# Set host to 0.0.0.0 so that it is accessible from 'outside the container'
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8001)))
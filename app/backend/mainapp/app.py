from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import os, sys
import pandas as pd
import pickle
from backend_functions.weather import get_weather
from backend_functions.coordinates import load_coordinates
#from backend_implementation.model import Model

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
	data = pd.read_csv("polygons_data.csv")
	
	global trained_model
	trained_model = pickle.load(open("models/model.sav", 'rb'))
	print("Server setup complete. The server can handle user requests now...", flush=True)


@app.route('/init', methods=['GET'])
def init():
	print(get_weather().head())
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
		year = form_values['predict_year']
		week = form_values['predict_week']
		print(f"POST request received for prediction. year: {year} and week: {week}", flush=True)
	else:
		print(f"GET request received for prediction. Using default values: {year} {week}", flush=True)

	# Store the user input
	user_input = UserInput(year, week)

	# Update the df with the year and week input by the user
	data.update_df_with_user_input(user_input)

	# Encode X_test as per the steps followed during model training
	data.perform_feature_encoding()

	# Make the predictions
	predictions = trained_model.make_predictions(data, year, week)

	return render_template('predictions.html', data=predictions)

@app.route('/visualise_past_data', methods=['POST', 'GET'])
def visualise_past_data(year='2015.0', week='1'):

	if request.method == 'POST':
		form_values = request.form.to_dict()
		year = form_values['past_year']
		week = form_values['past_week']
		print(f"POST request received for past data. year: {year} and week: {week}", flush=True)
	
	year = float(year)
	week = float(week)
	response = data.query_for_past_date(year, week)
	return render_template('past_visualisation.html', data=response)

# Set host to 0.0.0.0 so that it is accessible from 'outside the container'
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8001)))
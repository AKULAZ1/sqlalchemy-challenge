# Import the dependencies.
import numpy as np 
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with = engine)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind = engine)

#################################################
# Flask Setup
#################################################

#Initialize the Flask Climate App 
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Homepage- List all the avialable routes on the Climate App
@app.route("/")
def home():
    return(
        f"Welcome to the Climate API Homepage! <br>"
        f"Here are all the available routes: <br>"
        f"- Home (/) <br>"
        f"- Precepitation (/api/v1.0/precipitation) <br>"
        f"- Stations (/api/v1.0/stations) <br>"
        f"- Temperature Observations (/api/v1.0/tobs) <br>"
        f"- Dynamic Route- "
    )

#Precipitation Page
@app.route("/api/v1.0/precipitation")
def prcp():
    #Query the last year of temperature observations
    year_ago = dt.date(2017,8,23) - dt.timedelta(days = 365)
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).order_by(measurement.date).all()
  
    #Convert query results to a dictionary where the "Key" is date and the "Value" is prcp
    prcp_dict = {}
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    
    #Return a JSON representation of the dictionary
    return jsonify(prcp_dict)

#Stations Page 
@app.route("/api/v1.0/stations")
def stations():
    #Query all the stations in the datset
    stations = session.query(station.station).all()

    #Convert query results- list of tuples- into normal list
    all_stations = list(np.ravel(stations))

    #Return a JSON representation of the list
    return jsonify(all_stations)

#Temperature Observations Page 
@app.route("/api/v1.0/tobs")
def tobs():
    #Query the "most active" station
    activest = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()
    
    #Store the "most active" station's ID in a variable
    activestID = activest[0]

    #Query the last year of temperature observations for the "most active" station
    year_ago = dt.date(2017,8,23) - dt.timedelta(days = 365)
    activest_data = session.query(measurement.tobs).filter(measurement.station == activestID).filter(measurement.date >= year_ago).all()

    #Convert query results- list of tuples- into normal list
    activest_tobs = list(np.ravel(activest_data))

    #Return a JSON representation of the list
    return jsonify(activest_tobs)

#Dynamic Routes- Start and Start/End 
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dynamic(start = 0, end = 0):
    #Convert string in format YYYY-MM-DD to date 
    #The .datetime.strptime method below and again in line 118 was sourced from a Stack Overflow board.
    start_fmt = dt.datetime.strptime(start, '%Y-%m-%d')

    #Create a "Selection" to hold values to be queried depending on input date(s) 
    selection = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    
    #Create an if statement to determine whether to query from a given date to the end of the dataset 
    # or for a specified period of time (Start/End)
    if end == 0:
        #Query for "min", "max", and "avg" tobs from given date to end of dataset
        dynamic_data = session.query(*selection).filter(measurement.date >= start_fmt).all()
    else:
        #Convert string in format YYYY-MM-DD to date 
        end_fmt = dt.datetime.strptime(end, '%Y-%m-%d')

        #Query for "min", "max", and "avg" tobs for a specified period of time
        dynamic_data = session.query(*selection).filter(measurement.date >= start_fmt).filter(measurement.date <= end_fmt).all()
    
    #Convert query results- list of tuples- into normal list
    dynamic_tobs = list(np.ravel(dynamic_data))

    #Return a JSON representation of the list
    return jsonify(dynamic_tobs)

#App Run Statement
if __name__ == "__main__":
    app.run(debug=True)
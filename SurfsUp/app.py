# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

### I passed this to all routes below as well.
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Taken from climate_starter query
    date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date).all()
    session.close()

    # Create dictionary from data and add to a list
    precipitation = []
    for date,prcp  in results:
        dict = {}
        dict["date"] = date
        dict["prcp"] = prcp
           
    precipitation.append(dict)

    
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
        
    # Query all Stations
    results = session.query(Station.name).all()
    session.close()

    # Zip the tuple elements
    stations = list(zip(*results))[0]

    # Not sure why the above doesn't do the trick, but it works.
    stations = list(stations)

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for most active
    activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active = activity[0][0]

    # Query dates/temperature observations based on most active above
    tobs = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active).all()

    session.close()

    return jsonify(tobs)


@app.route('/api/v1.0/<start>')
def start(start_date):
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min/max/avg
    query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()

    tobs = []
    for min, max, avg in queryresult:
        dict = {}
        dict["Min"] = min
        dict["Max"] = max
        dict["Avg"] = avg
        tobs.append(dict)

    return jsonify(tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def end(start_date, end_date):    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min/max/avg
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
  
    tobs = []
    for min, max, avg in results:
        dict = {}
        dict["Min"] = min
        dict["Max"] = max
        dict["Avg"] = avg
        tobs.append(dict)     

    return jsonify(tobs)

if __name__ == "__main__":
    app.run(debug=True)

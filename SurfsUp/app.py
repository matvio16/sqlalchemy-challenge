# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# Get the value for a year prior to the last date in the dataset
def subtract_one_year():

    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_format = '%Y-%m-%d'
    old_date = dt.datetime.strptime(most_recent_date.date, date_format)
    earlier_year = old_date - dt.timedelta(days=365)
    session.close()

    return(earlier_year)

#################################################
# Flask Routes
#################################################

# List all the available routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
    )

# Return the JSON representation of the precipitation analysis
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    year_earlier = subtract_one_year()

    session = Session(engine)
# Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_earlier).all()

    session.close()

    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

# Return the JSON list of the stations
@app.route("/api/v1.0/stations")
def station():

    session = Session(engine)

    """List of all stations"""
    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


# Return the JSON representation of the most active station's temperature by date
@app.route("/api/v1.0/tobs")
def tobs():
    
    year_earlier = subtract_one_year()

    session = Session(engine)
# Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc())
    most_obs = results.first().station
    most_query = session.query(Measurement.tobs).order_by(Measurement.date).\
        filter(Measurement.date >= year_earlier).filter(Measurement.station == most_obs).all()

    session.close()

    all_tobs = list(np.ravel(most_query))

    return jsonify(all_tobs)

# Return min temp, average temp and max temp from a start date
@app.route("/api/v1.0/<start>")
def start(start):
    """List min temp, average temp and max temp."""
    results = session.query(func.min(Measurement.tobs).label("min"), func.avg(Measurement.tobs).label("avg"), func.max(Measurement.tobs).label("max")).\
        group_by(Measurement.date).filter(Measurement.date >= start).all()
    
    session.close()
    stats = []
    for min, avg, max in results:
        stats_dict = {}
        stats_dict["TMIN"] = min
        stats_dict["TAVG"] = avg
        stats_dict["TMAX"] = max
        stats.append(stats_dict)

    return jsonify(stats)

# Return min temp, average temp and max temp in a date range
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """List min temp, average temp and max temp."""
    results = session.query(func.min(Measurement.tobs).label("min"), func.avg(Measurement.tobs).label("avg"), func.max(Measurement.tobs).label("max")).\
        group_by(Measurement.date).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    stats = []
    for min, avg, max in results:
        stats_dict = {}
        stats_dict["TMIN"] = min
        stats_dict["TAVG"] = avg
        stats_dict["TMAX"] = max
        stats.append(stats_dict)

    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True)
# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
import numpy as np
import pandas as pd
import datetime as dt


from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/brian.stumm/Desktop/School-Bootcamp/Class_files/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
Base.classes.keys()

# Save references to each table
measure = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end</br>"

    )


# Precipitation measurements for the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    lastdate = session.query(func.max(measure.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    results = session.query(measure.date, measure.prcp).\
            filter(measure.date.between(startdate,lastdate)).\
            all()
    
    precip = []
    for date, prcp in results:
            precip_dict ={}
            precip_dict['date'] = date
            precip_dict['prcp'] = prcp
            precip.append(precip_dict)
    return jsonify(precip)


# List of all the stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

#Temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    top_station = session.query(measure.station).\
                    group_by(measure.station).\
                    order_by(func.count(measure.station).desc()).\
                    subquery()
    lastdate = session.query(func.max(measure.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    results = session.query(measure.date, measure.tobs).\
                filter(measure.date.between(startdate,lastdate)).\
                filter(measure.station.in_(top_station)).\
                all()

    topStation = []
    for date, tobs in results:
            tobs_dict ={}
            tobs_dict['date'] = date
            tobs_dict['tobs'] = tobs
            topStation.append(tobs_dict)
    return jsonify(topStation)


#list of the minimum temperature, the average temperature, and the maximum temperature 
# for a specified start or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def rangestart(start,end=None):
    session=Session(engine)
    if end == None:
        enddate = session.query(func.max(measure.date)).\
                    scalar()
    else:
        enddate = dt.datetime.strptime(end, "%m-%d-%Y")
        startdate = dt.datetime.strptime(start, "%m-%d-%Y")
    results = session.query(func.min(measure.tobs).label('min_temp'),
                            func.avg(measure.tobs).label('avg_temp'),
                            func.max(measure.tobs).label('max_temp')).\
                filter(measure.date.between(startdate,enddate)).\
                first()
 
    datapoints = list(np.ravel(results))
    return jsonify(datapoints)

if __name__ == "__main__":
    app.run(debug=False)
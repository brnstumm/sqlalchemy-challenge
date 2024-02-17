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
app=Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (f"""
<H1> <center> <strong> Welcome to the weather API! </strong> </center> </H1> <br>
<center>/precipitation</center><br>
<center>/stations</center><br>
<center>/tobs</center><br>
<center>/start</center><br>
<center>/start/yyyy-mm-dd</center><br>
""")

@app.route("/precipitation")
def precipitation():
    session = Session(engine)
    
    recentdate = session.query(func.max(Measurement.date)).\
                    scalar()
    recent_date = dt.datetime.strptime(recentdate,"%Y-%m-%d").date()
    beginning_date = recent_date - dt.timedelta(days=365)
    oneyearpast = beginning_date.strftime("%Y-%m-%d")
    prcp_data=session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=oneyearpast).all()
    
    session.close()
    
    precipitation = []
    for date, prcp in prcp_data:
            precipitation_dict ={}
            precipitation_dict['date'] = date
            precipitation_dict['prcp'] = prcp
            precipitation.append(precipitation_dict)
    return jsonify(list(np.ravel(precipitation)))


@app.route("/stations")
def stations():
    results=session.query(Station.station).all()
    session.close()
    return(list(np.ravel(results)))


@app.route("/tobs")
def tobs():
    session = Session(engine)
    
    recentdate = session.query(func.max(Measurement.date)).\
                    scalar()
    recent_date = dt.datetime.strptime(recentdate,"%Y-%m-%d").date()
    beginning_date = recent_date - dt.timedelta(days=365)
    oneyearpast = beginning_date.strftime("%Y-%m-%d")
    prcp_data=session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date>=oneyearpast).all()
    
    session.close()
    
    temp = []
    for date, tobs in prcp_data:
            temp_dict ={}
            temp_dict['date'] = date
            temp_dict['tobs'] = tobs
            temp.append(temp_dict)
    return jsonify(list(np.ravel(temp))) #return jsonify(temp)

@app.route("/<start>")
@app.route("/<start>/<end>")
def stats(start=None,end=None):
    temp_stats=[func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    if not end:
        results=session.query(*temp_stats).filter(Measurement.date>=start).all()
        session.close()
        return jsonify(list(np.ravel(results)))
    results=session.query(*temp_stats).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    session.close()
    return jsonify(list(np.ravel(results)))
    


if __name__=="__main__":
    app.run()
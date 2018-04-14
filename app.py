################################
###########FLASK API############
################################

### IMPORT STATMENTS ###
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

######################
### DATABASE SETUP ###
######################
engine = create_engine("sqlite:///hawaii.sqlite")

### REFLECTION ###
Base = automap_base()
Base.prepare(engine, reflect =  True)

### TABLE REFERENCE ###
Measurement = Base.classes.measurements
Station = Base.classes.stations

session = Session(engine)

###################
### FLASK SETUP ###
###################
app = Flask(__name__)

### ROUTES ###

@app.route("/")
def homepage():
    return(
        f"Hawaii Weather Repository API<br/>"
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precip():

    last_yr_dt = dt.date.today() - dt.timedelta(days = 365)

    rainfall = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_yr_dt).all()

    rfall_dict = {date: prcp for date, prcp in rainfall}
    return jsonify(rfall_dict)

@app.route("/api/v1.0/stations")
def station():
    all_stations = session.query(Station.stations).all()
    station_list = list(np.ravel(all_stations))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs_monthly():
    last_yr_dt =  dt.date.today() - dt.timedelta(days = 365)
    temps_obsvd = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date > last_yr_dt).all()

    temperatures = list(np.ravel(temps_obsvd))
    return jsonify(temperatures)
    
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_stats(start = None, end = None):
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*selection).\
            filter(Measurement.date >= start).all()
        
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    results = session.query(*selection).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run()
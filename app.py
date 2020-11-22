import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, Query
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind = engine)


#########################################
# import Flask
from flask import Flask

# Create an app, being sure to pass __name__
app = Flask(__name__)

#########################################


# Define what to do when a user hits the index route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Please put start date, or start/end date in the route below<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )



# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")

    # find the latest date
    all_date_data = (
                    Query(Measurement)
                    .with_session(session)
                    .with_entities(Measurement.date)
                    .all()
                    )
    lastest_date = all_date_data[len(all_date_data)-1].date

    # find 12 months from the latest date
    twl_mon_ago = dt.datetime.strptime(lastest_date, '%Y-%m-%d') - dt.timedelta(days=365)

    prcp_data = session.query(Measurement.date, func.avg(Measurement.prcp))\
        .filter(Measurement.date >= twl_mon_ago, Measurement.prcp !=None)\
            .group_by(Measurement.date).all()
    
    prcp_data_dict = dict(prcp_data)

    return jsonify(prcp_data_dict)


# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")

    # Query all stations
    station_all = (
                    Query(Measurement)
                    .with_session(session)
                    .with_entities(Measurement.station).distinct()
                    .all()
                    )            
    
    # List all stations
    station_all_list = list(station_all)

    return jsonify(station_all_list)


# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")

    # most active stations
    most_act_station = (
                    Query(Measurement)
                    .with_session(session)
                    .with_entities(Measurement.station, func.count(Measurement.station))
                    .group_by(Measurement.station)
                    .order_by(func.count(Measurement.station).desc())
                    .all()
                    )
                    
    top_sta_id = most_act_station[0][0]

    tobs_data_data = (
                        Query(Measurement)
                        .with_session(session)
                        .filter(Measurement.station == top_sta_id, Measurement.date >= '2016-08-23')
                        .with_entities(Measurement.date, Measurement.tobs)
                        .all()
    )
    
    tobs_data_list = list(tobs_data_data)
    
    return jsonify(tobs_data_list)

# Define what to do when a user hits the /api/v1.0/<start>
@app.route("/api/v1.0/<start>")
def start(start=None):
    print("Server received request for '/api/v1.0/<start>' page...")

    # most active stations
    start_date = (
                    Query(Measurement)
                    .with_session(session)
                    .filter(Measurement.date>=start)
                    .with_entities(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs))
                    .group_by(Measurement.date)
                    .all()
                    )
                    
    start_date_list = list(start_date)
    
    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    print("Server received request for '/api/v1.0/<start_end>' page...")

    # most active stations
    start_end_date = (
                    Query(Measurement)
                    .with_session(session)
                    .filter(Measurement.date>=start, Measurement.date<=end)
                    .with_entities(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs))
                    .group_by(Measurement.date)
                    .all()
                    )
                    
    start_end_date_list = list(start_end_date)
    
    return jsonify(start_end_date_list)


#########################################
if __name__ == "__main__":
    app.run(debug=True)
#########################################

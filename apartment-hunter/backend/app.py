from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'apartments.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)

Property = Base.classes.Property
Renter = Base.classes.Renter
LeasingOffice = Base.classes['Leasing Office']
LeaseApplication = Base.classes['Lease Application']
Review = Base.classes.Reviews
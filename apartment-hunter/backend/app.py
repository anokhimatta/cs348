import sqlite3
from flask import Flask, request, jsonify, g
from flask import CORS
import os
app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'apartments.db')

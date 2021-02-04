"""Main app/routing file for AIrBnB Price Finder."""

import json
import os
from os import getenv
from tempfile import mkdtemp

import numpy as np
import pandas as pd
from category_encoders import OrdinalEncoder
from flask import Flask, jsonify, render_template, request
from joblib import load
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

from .models import DB, Host, Listing


def create_app():

    # Instantiate flask app object
    app = Flask(__name__)

    # Set DB environment variables
    # getenv("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy DB
    DB.init_app(app)

    # Load features dictionary for passing into jinja templates and validation
    features = load_features()

    # Load prediction model
    airbnb_model = load("model.joblib")

    # Save data (for development purposes)
    listing = {}

    @app.route('/')
    def root():
        """WebApp home page"""
        # Show the actual lanfding page with fields to enter
        return render_template('predict-one.html', forms=features, title="Home")

    @app.route('/add_listing', methods=["GET", "POST"])
    def add_listing():
        """Add a new listing to the database"""
        if request.method == "POST":
            listing = get_input_data()
            # TODO - save listing into database
        return render_template('listing.html', title="Add a Listing", forms=features, message=f"{listing}")

    @app.route('/predict', methods=["POST"])
    def predict():
        """Uses trained model to make prediction on a given listing"""
        return render_template('predict.html', title='Home', message="Coming Soon")

    @app.route('/predict-one', methods=["GET", "POST"])
    def predict_one():
        """Uses trained model to make prediction on a given listing"""

        predict_message = "Please enter your listing details"
        # Retrieve and transform data from forms
        if request.method == "POST":
            listing = get_input_data()
            predicted_rate = get_prediction(airbnb_model, listing)
            predict_message = f"We suggest you set your price at ${predicted_rate:.2f}"

        return render_template('predict-one.html', title="Price Finder", forms=features, message=predict_message)

    @app.route('/reset')
    def reset():
        """Resets the Listings and Hosts tables only"""
        # TODO - Drop Listings and Hosts table, create all tables again
        return "Coming Soon!"

    # SECRET ROUTES

    @app.route('/examples')
    def examples():
        """Adds examples to the database"""
        # Model order: propertytype roomtype accom bathrooms bedtype cancell cleaning city inst numrev revscore bedrooms beds
        features_populated = {"property_type": ['Apartment'],
                              "room_type": ["Entire home/apt"],
                              "accommodates": [16],
                              "bathrooms": [8],
                              "bed_type": ['Real Bed'],
                              "cancellation_policy": ['strict'],
                              "cleaning_fee": [True],
                              "city": ['NYC'],
                              "instant_bookable": [True],
                              "number_of_reviews": [605],
                              "review_scores_rating": [100],
                              "bedrooms": [10],
                              "beds": [18]}

        test_array = pd.DataFrame(data=features_populated)
        airbnb_model = load("model.joblib")
        get_price = str(airbnb_model.predict(test_array))
        return get_price

    @app.route('/test-db')
    def test_db():
        DB.drop_all()
        DB.create_all()
        return "DB created"

    return app


def load_features():
    """Loads features file and returns a dictionary"""
    feature_order = get_feature_orders()
    with open('features.json') as file:
        all_possible = json.load(file)
        # Restrict feature dictionary to features used in the model
        features = {feature: all_possible[feature]
                    for feature in feature_order}
        return features


def get_feature_orders():
    """
    Returns an ordered list of features to use on webpage 
    and for model prediction (dataframe columns must be in correct order so that
    model.predict(dataframe) will perform correctly)
    """
    feature_order = [
        "bedrooms",
        "bathrooms",
        "zipcode",
        "room_type",
        "accommodates",
        "property_type",
        # "bed_type",
        # "cancellation_policy",
        # "cleaning_fee",
        # "city",
        # "instant_bookable",
        # "number_of_reviews",
        # "review_scores_rating",
        # "beds",
    ]
    return feature_order


def get_input_data():
    """
    Takes data input from website and returns a dictionary with valid data to be
    saved in database or passed into prediction model
    """
    listing = {}
    features = load_features()
    data = request.form.to_dict(flat=False)
    for key, value in data.items():
        if features[key]['type'] == "number":
            listing[key] = [float(value[0])]
        elif features[key]['type'] == "bool":
            listing[key] = [bool(value[0])]
        else:
            listing[key] = value

    return listing


def get_prediction(model, listing):
    """Takes a model and a listing and returns a prediction"""

    # Restrict to features used
    try:
        # will fail if data_types are not in the model
        data_types = {"cleaning_fee": bool, "instant_bookable": bool}
        df = (pd.DataFrame(listing).astype(data_types))[
            get_feature_orders()]
    except:
        df = pd.DataFrame(listing)[get_feature_orders()]

    return model.predict(df)[0]

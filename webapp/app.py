"""Main app/routing file for AIrBnB Price Finder."""

import json
import os
from os import getenv
from random import randint
from tempfile import mkdtemp

import numpy as np
import pandas as pd
from category_encoders import OrdinalEncoder
from flask import Flask, jsonify, render_template, request
from joblib import load
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

from .models import DB, Listing


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

    # @app.route('/')
    # def root():
    #     """WebApp home page"""
    #     # Show the actual lanfding page with fields to enter
    #     return render_template('predict-one.html', forms=features, title="Home")

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

    @app.route('/', methods=["GET", "POST"])
    def predict_one():
        """Uses trained model to make prediction on a given listing"""
        # Refresh features
        features = load_features()
        predict_message = "Please enter your listing details"
        # Retrieve and transform data from forms
        if request.method == "POST":
            # Get listing from web form
            listing = get_input_data()

            # Save listing for next web form
            update_default_features(listing)
            # Refresh features (for input forms)
            features = load_features()

            # Save listing in database
            DB.session.add(Listing(id=randint(0, 100_000), **listing))
            DB.session.commit()
            # Get predicted rate
            predicted_rate = get_prediction(
                airbnb_model, transform_input_data(listing))
            predict_message = f"We suggest you set your price at ${predicted_rate:.2f}"

        return render_template('predict-one.html', title="Price Finder", forms=features, message=predict_message)

    @app.route('/reset')
    def test_db():
        # reset last saved listing
        listing = {}
        # Reset database
        DB.drop_all()
        DB.create_all()
        return "DB created"

    # SECRET ROUTES

    @app.route('/examples')
    def examples():
        """Adds examples to the database"""
        # Model order: propertytype roomtype accom bathrooms bedtype cancell cleaning city inst numrev revscore bedrooms beds
        features_populated = {"property_type": ['Apartment'],
                              "room_type": ["Entire home/apt"],
                              "accommodates": [16],
                              "bathrooms": [8],
                              "bedrooms": [10],
                              "zipcode": 60176
                              }

        test_array = pd.DataFrame(data=features_populated)
        airbnb_model = load("model.joblib")
        get_price = str(airbnb_model.predict(test_array))
        return get_price

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
        "property_type",
        "room_type",
        "accommodates",
        "bedrooms",
        "baths",
        "zip",
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
            listing[key] = float(value[0])
        elif features[key]['type'] == "bool":
            listing[key] = bool(value[0])
        elif features[key]['type'] == "zip":
            listing[key] = int(value[0])
        else:
            listing[key] = value[0]

    return listing


def transform_input_data(data):
    """Transform input data dictionary into format ready to use with 
        model.predict"""
    return {key: [value] for key, value in data.items()}


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


def update_default_features(listing):
    """Updates features.json file with most recent listing"""
    # Open json file as dictionary
    with open('features.json', 'r') as file:
        data = json.load(file)
        # make necessary changes
        data['accommodates']['default'] = listing['accommodates']
        data['bedrooms']['default'] = listing['bedrooms']
        data['baths']['default'] = listing['baths']
        data['zip']['default'] = listing['zip']
        data['property_type']['default'] = listing['property_type']
        data['room_type']['default'] = listing['room_type']
    # Save dictionary to json file
    with open('features.json', 'w+') as file:
        json.dump(data, file)

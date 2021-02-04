"""Main app/routing file for AIrBnB Price Finder."""

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

    # Features used
    # Dictionary takes
    #   - label:            for displaying in listing.html
    #   - type:             for specifying what type of input form is needed
    #   - options:          if type is choice
    #   - min, max, step:   if type is number
    features = {
        "property_type": {"label": "Property Type",
                          "type": "choice",
                          "options": ['Apartment', 'House', 'Condominium',
                                      'Townhouse', 'Loft']
                          },
        "city": {"label": "City",
                 "type": "choice",
                 "options": ['NYC', 'LA', 'SF', 'DC', 'Chicago']},
        "room_type": {"label": "Room Type",
                      "type": "choice",
                      "options": ['Entire home/apt', 'Private room', 'Shared room']},
        "accommodates": {"label": "Accommodates",
                         "type": "number",
                         "min": 0,
                         "max": 16,
                         "step": 1},
        "bedrooms": {"label": "Bedrooms",
                     "type": "number",
                     "min": 0,
                     "max": 10,
                     "step": 1},
        "beds": {"label": "Beds",
                 "type": "number",
                 "min": 0,
                 "max": 18,
                 "step": 1},
        "bathrooms": {"label": "Bathrooms",
                      "type": "number",
                      "min": 0,
                      "max": 8,
                      "step": 0.5},
        "bed_type": {"label": "Bed Type",
                     "type": "choice",
                     "options": ['Real Bed', 'Futon', 'Pull-out Sofa',
                                 'Airbed', 'Couch']},
        "cancellation_policy": {"label": "Cancellation Policy",
                                "type": "choice",
                                "options": ['strict', 'flexible', 'moderate',
                                            'super_strict_30',
                                            'super_strict_60']},
        "cleaning_fee": {"label": "Cleaning Fee?",
                         "type": "bool",
                         "options": ['True', 'False']},
        "instant_bookable": {"label": "Instant Bookable?",
                             "type": "bool",
                             "options": ['True', 'False']},
        "number_of_reviews": {"label": "Number of Reviews",
                              "type": "number",
                              "min": 0,
                              "max": 605},
        "review_scores_rating": {"label": "Review Scores Rating",
                                 "type": "number",
                                 "min": 20,
                                 "max": 100},
    }

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
            data = request.form.to_dict(flat=False)
            for key, value in data.items():
                listing[key] = value
            # TODO - save listing into database
        return render_template('listing.html', title="Add a Listing", forms=features, message=f"{listing}")

    @app.route('/predict', methods=["POST"])
    def predict():
        """Uses trained model to make prediction on a given listing"""
        return render_template('predict.html', title='Home', message="Coming Soon")

    @app.route('/predict-one', methods=["GET", "POST"])
    def predict_one():
        """Uses trained model to make prediction on a given listing"""
        feature_order = ["property_type",
                         "room_type",
                         "accommodates",
                         "bathrooms",
                         "bed_type",
                         "cancellation_policy",
                         "cleaning_fee",
                         "city",
                         "instant_bookable",
                         "number_of_reviews",
                         "review_scores_rating",
                         "bedrooms",
                         "beds"]
        airbnb_model = load("model.joblib")
        predict_message = f"{listing}"
        # Retrieve and transform data from forms
        if request.method == "POST":
            data = request.form.to_dict(flat=False)
            for key, value in data.items():
                if features[key]['type'] == "number":
                    listing[key] = [float(value[0])]
                elif features[key]['type'] == "bool":
                    listing[key] = [bool(value[0])]
                    print(listing[key])
                else:
                    listing[key] = value
            data_types = {"cleaning_fee": bool, "instant_bookable": bool}
            df = pd.DataFrame(data)[feature_order].astype(data_types)

            get_price = airbnb_model.predict(df)[0]
            predict_message = f"We suggest you set your price at ${get_price:.2f}"

        return render_template('predict-one.html', title="Price Finder", forms=features, message=predict_message)

    @ app.route('/reset')
    def reset():
        """Resets the Listings and Hosts tables only"""
        # TODO - Drop Listings and Hosts table, create all tables again
        return "Coming Soon!"

    # SECRET ROUTES

    @ app.route('/examples')
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

    @ app.route('/test-db')
    def test_db():
        DB.drop_all()
        DB.create_all()
        return "DB created"

    return app

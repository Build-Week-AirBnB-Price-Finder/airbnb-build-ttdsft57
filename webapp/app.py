"""Main app/routing file for AIrBnB Price Finder."""

from os import getenv

from flask import Flask, render_template

from .models.hosts import Host, Listing


def create_app():

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

    @app.route('/')
    def root():
        """WebApp home page"""
        return render_template('index.html', title="Home")

    @app.route('/add_listing')
    def add_listing():
        """Add a new listing to the database"""
        return render_template('listing.html', title="Add a Listing", message="Coming Soon!")

    @app.route('/predict', methods=["POST"])
    def predict():
        """Uses trained model to make prediction on a given listing"""
        # TODO - Import model and run prediction on listing features
        return "Coming Soon!"

    @app.route('/reset')
    def reset():
        """Resets the Listings and Hosts tables only"""
        # TODO - Drop Listings and Hosts table, create all tables again
        return "Coming Soon!"

    # SECRET ROUTES

    @app.route('/examples')
    def examples():
        """Adds examples to the database"""
        return "Not this time", 404

    return app

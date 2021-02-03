"""Main app/routing file for AIrBnB Price Finder."""

from os import getenv

from flask import Flask, render_template, request

from .models.hosts import Host, Listing


def create_app():

    # Instantiate flask app object
    app = Flask(__name__)

    # Set DB environment variables
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

    # Save data (for development purposes)
    listing = {}

    @app.route('/')
    def root():
        """WebApp home page"""
        return render_template('index.html', title="Home")

    @app.route('/add_listing', methods=["GET", "POST"])
    def add_listing():
        """Add a new listing to the database"""
        if request.method == "POST":
            data = request.form.to_dict(flat=False)
            print(data)
            for key, value in data.items():
                print(key, value)
                listing[key] = value
            print(listing)
        return render_template('listing.html', title="Add a Listing", message=f"{listing}")

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

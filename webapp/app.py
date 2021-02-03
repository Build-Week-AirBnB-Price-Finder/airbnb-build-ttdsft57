"""Main app/routing file for AIrBnB Price Finder."""

from os import getenv

from flask import Flask, render_template, request

from .models.hosts import Host, Listing


def create_app():

    # Instantiate flask app object
    app = Flask(__name__)

    # Set DB environment variables
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # TODO - convert features list into a features dictionary where the features
    #       are the keys and the values are:
    #           - lists of possible categories for categorical features
    #           - default values for continuous quantitative features
    #       Then change the /add_listing and listing.html to accept a dictionary
    #           in order to create the input forms
    features = ["id", "room_type", "accommodates", "bathrooms", "bed_type",
                "cancellation_policy", "cleaning_fee", "city",
                "instant_bookable", "number_of_reviews", "review_scores_rating",
                "bedrooms", "beds"]

    # Save data (for development purposes)
    listing = {}

    @app.route('/')
    def root():
        """WebApp home page"""
        # Show the actual lanfding page with fields to enter
        return render_template('index.html', title="Home")

    @app.route('/add_listing', methods=["GET", "POST"])
    def add_listing():
        """Add a new listing to the database"""
        if request.method == "POST":
            data = request.form.to_dict(flat=False)
            for key, value in data.items():
                listing[key] = value[0]
            # TODO - save listing into database
        return render_template('listing.html', title="Add a Listing", forms=features, message=f"{listing}")

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

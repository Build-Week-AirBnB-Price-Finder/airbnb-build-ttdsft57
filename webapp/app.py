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

    # Features used
    # Dictionary takes
    #   - label:            for displaying in listing.html
    #   - type:             for specifying what type of input form is needed
    #   - options:          if type is choice
    #   - min, max, step:   if type is number
    features = {
        "city": {"label": "City",
                 "type": "choice",
                 "options": ['NYC', 'LA', 'SF', 'DC', 'Chicago']},
        "room_type": {"label": "Room Type",
                      "type": "choice",
                      "options": ['Apartment', 'House', 'Condominium',
                                  'Townhouse', 'Loft']},
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
                         "type": "choice",
                         "options": ['true', 'false']},
        "instant_bookable": {"label": "Instant Bookable?",
                             "type": "choice",
                             "options": ['t', 'f']},
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

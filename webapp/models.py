"""SQLAlchemy models for AIrBnB listings"""

from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


# Listing Table
class Listing(DB.Model):
    """AIrBnB listings corresponding to Hosts"""
    id = DB.Column(DB.Integer, primary_key=True)
    property_type = DB.Column(DB.String, nullable=False)
    room_type = DB.Column(DB.String, nullable=False)
    accommodates = DB.Column(DB.Integer, nullable=False)
    bedrooms = DB.Column(DB.Integer, nullable=False)
    baths = DB.Column(DB.Numeric, nullable=False)
    zip = DB.Column(DB.Integer, nullable=False)

    def __repr__(self):
        # TODO - Replace self.id with more descriptive location information
        rep = f"""<Listing: Property Type - {self.property_type}, Zipcode - {self.zipcode}>"""
        return rep

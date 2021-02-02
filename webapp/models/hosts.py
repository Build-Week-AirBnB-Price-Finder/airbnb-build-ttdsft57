"""SQLAlchemy models for AIrBnB hosts"""

from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


# Host Table
class Host(DB.Model):
    """AIrBnB hosts corresponding to Listings"""
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String, nullable=False)

    def __repr__(self):
        return f"<Host: {self.name}>"


# Listing Table
class Listing(DB.Model):
    """AIrBnB listings corresponding to Hosts"""
    id = DB.Column(DB.Integer, primary_key=True)
    # TODO - add columns used as features in model

    # Establish relationship with Host table
    host_id = DB.Column(DB.Integer, DB.ForeignKey("host.id"), nullable=False)
    host = DB.relationship("Host", backref=DB.backref("listings", lazy=True))

    def __repr__(self):
        # TODO - Replace self.id with more descriptive location information
        return f"<Listing: {self.id}>"

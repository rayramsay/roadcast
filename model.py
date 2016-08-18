# This code is based on my implementation of Hackbright's Ratings exercise,
# which I pair-programmed with Jennifer Griffith-Delgado (gh: jgriffith23).

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc).

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User object for RoadCast website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    fname = db.Column(db.String(64), nullable=True)
    lname = db.Column(db.String(64), nullable=True)

    def __repr__(self):
        """Provide a human-readable representation of an instance of a user."""

        return "<User user_id=%s email=%s password=%s fname=%s lname=%s>" % \
            (self.user_id, self.email, self.password, self.fname, self.lname)


class Addr(db.Model):
    """Address object for RoadCast website."""

    __tablename__ = "addrs"

    addr_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Google Maps docs suggest storing each coord as FLOAT(10, 6)
    # https://developers.google.com/maps/articles/phpsqlajax_v3#createtable

    lat = db.Column(db.Float(10), nullable=False)
    lng = db.Column(db.Float(10), nullable=False)

    def __repr__(self):
        """Provide a human-readable representation of an instance of an address."""

        return "<Addr addr_id=%s lat=%s lng=%s>" % \
            (self.addr_id, self.lat, self.lng)


class Label(db.Model):
    """Label object for RoadCast website."""

    __tablename__ = "labels"

    label_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Make addr_id and user_id foreign keys, so we can create relationships
    # for labels -> addresses and labels -> users.
    addr_id = db.Column(db.Integer,
                        db.ForeignKey("addrs.addr_id"),
                        nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)

    label = db.Column(db.String(128), nullable=False)

    # Define relationship between labels and users
    user = db.relationship("User", backref=db.backref("labels",
                                                      order_by=label_id))

    # Define relationship between labels and addresses
    addr = db.relationship("Addr", backref=db.backref("labels",
                                                      order_by=label_id))

    def __repr__(self):
        """Provide a human-readable representation of an instance of a label."""

        return "<Label label_id=%s addr_id=%s user_id=%s label=%s>" % \
            (self.label_id, self.addr_id, self.user_id, self.label)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///roadcast'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

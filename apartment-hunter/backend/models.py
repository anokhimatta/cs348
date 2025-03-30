from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LeasingOffice(db.Model):
    __table_name__ = "Leasing Office"
    __table_args__ = {'extend_existing': True}

class LeaseApplications(db.Model):
    __table_name__ = "Lease Applications"
    __table_args__ = {'extend_existing': True}


class Property(db.Model):
    __table_name__ = "Property"
    __table_args__ = {'extend_existing': True}

class Renter(db.Model):
    __table_name__ = "Renter"
    __table_args__ = {'extend_existing': True}

class Review(db.Model):
    __table_name__ = "Review"
    __table_args__ = {'extend_existing': True}

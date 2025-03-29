from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LeasingOffice(db.Model):
    __table_name__ = "Leasing Office"
    office_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    address = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    open_hour = db.Column(db.Integer, nullable=False)
    close_hour = db.Column(db.Integer, nullable=False)

class LeaseApplications(db.Model):
    __table_name__ = "Lease Applications"
    application_id = db.Column("application_id", db.Integer, primary_key=True, unique=True, nullable=False)
    renter_id = db.Column("app_renter_id", db.Integer, db.ForeignKey('Renter.renter_id'), nullable=False)
    property_id = db.Column("app_property_id", db.Integer, db.ForeignKey('Property.property_id'), nullable=False)
    status = db.Column(db.String, nullable=False)

    renter = db.relationship("Renter", backref="applications")
    property = db.relationship("Property", backref="applications")





# CREATE TABLE "Leasing Office" (
#	"office_id"	INTEGER NOT NULL UNIQUE,
#	"name"	TEXT NOT NULL UNIQUE,
#	"address"	TEXT NOT NULL UNIQUE,
#	"email"	TEXT NOT NULL UNIQUE,
#	"phone_number"	INTEGER NOT NULL UNIQUE,
#	"open_hour"	INTEGER NOT NULL,
#	"close_hour"	INTEGER NOT NULL,
#	PRIMARY KEY("office_id")
#)

# CREATE TABLE "Lease Applications" (
#	"application_id"	INTEGER NOT NULL UNIQUE,
#	"app_renter_id"	INTEGER NOT NULL,
#	"app_property_id"	INTEGER NOT NULL,
#	"status"	TEXT NOT NULL,
#	CONSTRAINT "app_property_id" FOREIGN KEY("app_property_id") REFERENCES "Property"("property_id"),
#	CONSTRAINT "app_renter_id" FOREIGN KEY("app_renter_id") REFERENCES "Renter"("renter_id")
#)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LeaseApplications(db.Model):
    __table_name__ = "Lease Applications"
    application_id = db.Column("application_id", db.Integer, primary_key=True, unique=True, nullable=False)
    renter_id = db.Column("app_renter_id", db.Integer, db.ForeignKey('Renter.renter_id'), nullable=False)
    property_id = db.Column("app_property_id", db.Integer, db.ForeignKey('Property.property_id'), nullable=False)
    status = db.Column(db.String, nullable=False)

    # Relationships (Optional, if you want to access related data easily)
    renter = db.relationship("Renter", backref="applications")
    property = db.relationship("Property", backref="applications")




# CREATE TABLE "Lease Applications" (
#	"application_id"	INTEGER NOT NULL UNIQUE,
#	"app_renter_id"	INTEGER NOT NULL,
#	"app_property_id"	INTEGER NOT NULL,
#	"status"	TEXT NOT NULL,
#	CONSTRAINT "app_property_id" FOREIGN KEY("app_property_id") REFERENCES "Property"("property_id"),
#	CONSTRAINT "app_renter_id" FOREIGN KEY("app_renter_id") REFERENCES "Renter"("renter_id")
#)
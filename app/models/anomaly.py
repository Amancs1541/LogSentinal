from app.extensions import db

class Anomaly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.String(128), index=True)
    severity = db.Column(db.String(16), default="medium")
    description = db.Column(db.String(255))
    log_id = db.Column(db.Integer, db.ForeignKey("log_entry.id"))
    log = db.relationship("LogEntry", backref="anomalies")

from app.extensions import db
from datetime import datetime

class LogFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_entries = db.Column(db.Integer, default=0)

    entries = db.relationship("LogEntry", backref="logfile", lazy=True)

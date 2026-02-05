from app.extensions import db

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(32), index=True)
    username = db.Column(db.String(64), index=True)
    ip_address = db.Column(db.String(64), index=True)
    status = db.Column(db.String(32), index=True)
    raw_line = db.Column(db.Text)

    logfile_id = db.Column(db.Integer, db.ForeignKey("log_file.id"))

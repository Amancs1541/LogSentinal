from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import text
from app.models.log_entry import LogEntry
from app.models.anomaly import Anomaly
from app.models.log_file import LogFile
from app.extensions import db

anomalies_bp = Blueprint("anomalies", __name__)


@anomalies_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@anomalies_bp.route("/api/stats")
def stats():
    severity_filter = request.args.get("severity")

    total_logs = LogFile.query.count()
    total_entries = LogEntry.query.count()
    total_anomalies = Anomaly.query.count()

    rows = db.session.execute(text("""
        SELECT substr(timestamp, 1, 10) AS day,
               SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) AS success_count,
               SUM(CASE WHEN status='FAIL' THEN 1 ELSE 0 END) AS fail_count
        FROM log_entry
        GROUP BY day
        ORDER BY day
    """)).fetchall()

    days = [r[0] for r in rows]
    success_counts = [r[1] for r in rows]
    fail_counts = [r[2] for r in rows]

    ip_rows = db.session.execute(text("""
        SELECT ip_address, COUNT(*) AS cnt
        FROM log_entry
        GROUP BY ip_address
        ORDER BY cnt DESC
        LIMIT 7
    """)).fetchall()

    ips = [r[0] for r in ip_rows]
    ip_counts = [r[1] for r in ip_rows]

    anomaly_query = Anomaly.query
    if severity_filter:
        anomaly_query = anomaly_query.filter_by(severity=severity_filter)
    anomalies = anomaly_query.order_by(Anomaly.id.desc()).limit(100).all()

    anomaly_list = [
        {
            "rule": a.rule,
            "severity": a.severity,
            "description": a.description,
            "timestamp": a.log.timestamp if a.log else "",
            "ip": a.log.ip_address if a.log else "",
            "user": a.log.username if a.log else "",
        }
        for a in anomalies
    ]

    recent_logs = LogFile.query.order_by(LogFile.uploaded_at.desc()).limit(5).all()
    recent_logs_list = [
        {
            "id": log.id,
            "filename": log.filename,
            "uploaded_at": log.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "entries": log.total_entries
        }
        for log in recent_logs
    ]

    return jsonify(
        {
            "total_logs": total_logs,
            "total_entries": total_entries,
            "total_anomalies": total_anomalies,
            "days": days,
            "success_counts": success_counts,
            "fail_counts": fail_counts,
            "ips": ips,
            "ip_counts": ip_counts,
            "anomalies": anomaly_list,
            "recent_logs": recent_logs_list,
        }
    )

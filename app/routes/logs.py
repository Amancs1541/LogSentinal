from flask import (
    Blueprint, current_app, request, redirect,
    url_for, flash, render_template, jsonify
)
from sqlalchemy import text

from app.services.file_service import save_uploaded_file
from app.services.parser_service import (
    get_sample_lines,
    guess_fields_from_sample,
    parse_with_mapping,
    parse_universal,
)
from app.services.anomaly_service import run_anomaly_detection
from app.models.log_file import LogFile
from app.models.log_entry import LogEntry
from app.extensions import db

logs_bp = Blueprint("logs", __name__)

# ---------------------------------------------------------
# UPLOAD → SHOW FIELD MAPPING
# ---------------------------------------------------------

@logs_bp.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("logfile")
    if not file or file.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("main.index"))

    filepath, filename = save_uploaded_file(file, current_app.config["UPLOAD_FOLDER"])

    logfile = LogFile(filename=filename)
    db.session.add(logfile)
    db.session.commit()

    samples = get_sample_lines(filepath)
    if not samples:
        flash("No readable lines found.", "danger")
        return redirect(url_for("main.index"))

    sample_line = samples[0]
    parts, _ = guess_fields_from_sample(sample_line)

    return render_template(
        "map_fields.html",
        filepath=filepath,
        logfile_id=logfile.id,
        sample_line=sample_line,
        fields=list(enumerate(parts)),
    )

# ---------------------------------------------------------
# PROCESS LOG AFTER MAPPING / AUTO MODE
# ---------------------------------------------------------

@logs_bp.route("/process", methods=["POST"])
def process():
    filepath = request.form.get("filepath")
    logfile_id = int(request.form.get("logfile_id"))
    mode = request.form.get("mode", "mapping")

    logfile = LogFile.query.get_or_404(logfile_id)

    if mode == "auto":
        parsed_count = parse_universal(filepath, logfile_id)
    else:
        def idx(name):
            try: return int(request.form.get(name, -1))
            except: return -1

        mapping = {
            "timestamp_index": idx("timestamp_index"),
            "username_index": idx("username_index"),
            "ip_index": idx("ip_index"),
            "status_index": idx("status_index"),
        }

        parsed_count = parse_with_mapping(filepath, logfile_id, mapping)

    logfile.total_entries = parsed_count
    db.session.commit()

    run_anomaly_detection()

    flash(f"Processed {parsed_count} entries.", "success")
    return redirect(url_for("logs.list_logs"))

# ---------------------------------------------------------
# LIST LOG FILES
# ---------------------------------------------------------

@logs_bp.route("/list")
def list_logs():
    logs = LogFile.query.order_by(LogFile.uploaded_at.desc()).all()
    return render_template("logs_list.html", logs=logs)

# ---------------------------------------------------------
# DELETE LOG
# ---------------------------------------------------------

@logs_bp.route("/delete/<int:log_id>", methods=["POST"])
def delete_log(log_id):
    logfile = LogFile.query.get_or_404(log_id)

    LogEntry.query.filter_by(logfile_id=log_id).delete()

    from app.models.anomaly import Anomaly
    Anomaly.query.filter(
        Anomaly.log_id.in_(
            db.session.query(LogEntry.id).filter_by(logfile_id=log_id)
        )
    ).delete()

    db.session.delete(logfile)
    db.session.commit()

    flash("Log deleted.", "success")
    return redirect(url_for("anomalies.dashboard"))

# ---------------------------------------------------------
# LOG DETAIL
# ---------------------------------------------------------

@logs_bp.route("/<int:log_id>")
def log_detail(log_id):
    logfile = LogFile.query.get_or_404(log_id)

    total = logfile.total_entries
    success = LogEntry.query.filter_by(logfile_id=log_id, status="200").count()
    fail = LogEntry.query.filter(
        LogEntry.logfile_id == log_id,
        LogEntry.status != "200"
    ).count()

    ip_rows = db.session.execute(text("""
        SELECT ip_address, COUNT(*) 
        FROM log_entry
        WHERE logfile_id = :id
        GROUP BY ip_address
        ORDER BY COUNT(*) DESC
        LIMIT 7
    """), {"id": log_id}).fetchall()

    ips = [r[0] for r in ip_rows]
    ip_counts = [r[1] for r in ip_rows]

    entries = LogEntry.query.filter_by(logfile_id=log_id).limit(100).all()

    return render_template(
        "log_detail.html",
        logfile=logfile,
        total=total,
        success=success,
        fail=fail,
        ips=ips,
        ip_counts=ip_counts,
        entries=entries,
    )

# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

@logs_bp.route("/search/<int:log_id>")
def search_entries(log_id):
    q = request.args.get("q", "")
    results = LogEntry.query.filter(
        LogEntry.logfile_id == log_id,
        LogEntry.raw_line.ilike(f"%{q}%")
    ).all()

    return jsonify([
        {
            "timestamp": r.timestamp,
            "user": r.username,
            "ip": r.ip_address,
            "status": r.status,
            "raw": r.raw_line
        }
        for r in results
    ])

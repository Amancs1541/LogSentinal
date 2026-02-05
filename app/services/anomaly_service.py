from datetime import time, datetime
from collections import defaultdict
from app.extensions import db
from app.models.log_entry import LogEntry
from app.models.anomaly import Anomaly

def run_anomaly_detection():
    db.session.query(Anomaly).delete()

    # Rule 1: multiple failed logins from same IP+user
    failed_logs = (
        LogEntry.query.filter_by(status="FAIL")
        .order_by(LogEntry.ip_address, LogEntry.username, LogEntry.id)
        .all()
    )
    fail_counter = defaultdict(int)
    for log in failed_logs:
        key = (log.ip_address, log.username)
        fail_counter[key] += 1
        if fail_counter[key] == 5:
            anomaly = Anomaly(
                rule="MULTIPLE_FAILED_LOGINS",
                severity="high",
                description=f"5 failed logins for user {log.username} from IP {log.ip_address}",
                log=log,
            )
            db.session.add(anomaly)

    # Rule 2: successful login at unusual time (00:00–04:00)
    night_start = time(0, 0, 0)
    night_end = time(4, 0, 0)
    success_logs = LogEntry.query.filter_by(status="SUCCESS").all()
    for log in success_logs:
        ts = datetime.strptime(log.timestamp, "%Y-%m-%d %H:%M:%S")
        if night_start <= ts.time() <= night_end:
            anomaly = Anomaly(
                rule="UNUSUAL_LOGIN_TIME",
                severity="medium",
                description=f"Successful login at unusual time: {log.timestamp}",
                log=log,
            )
            db.session.add(anomaly)

    # Rule 3: suspicious IP with many mixed events
    ip_counts = (
        db.session.query(LogEntry.ip_address, db.func.count(LogEntry.id))
        .group_by(LogEntry.ip_address)
        .having(db.func.count(LogEntry.id) > 50)
        .all()
    )
    for ip, cnt in ip_counts:
        anomaly = Anomaly(
            rule="HIGH_ACTIVITY_IP",
            severity="medium",
            description=f"IP {ip} generated {cnt} events.",
            log=None,
        )
        db.session.add(anomaly)

    db.session.commit()

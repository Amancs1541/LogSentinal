import re
from app.extensions import db
from app.models.log_entry import LogEntry

# ---------------------------------------------------------
# REGEX PATTERNS FOR AUTO-DETECTION
# ---------------------------------------------------------

APACHE_PATTERN = re.compile(
    r'(?P<ip>\S+)\s+\S+\s+(?P<user>\S+)\s+'
    r'\[(?P<timestamp>.*?)\]\s+'
    r'"(?P<method>\S+)\s+(?P<path>\S+)\s+\S+"\s+'
    r'(?P<status>\d{3})\s+(?P<size>\d+)'
)
SSH_PATTERN = re.compile(
    r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
    r'(?P<host>\S+)\s+sshd\[\d+\]:\s+'
    r'(?P<message>.*?)(?:\s+from\s+(?P<ip>\d+\.\d+\.\d+\.\d+))?'
)

SYSLOG_PATTERN = re.compile(
    r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
    r'(?P<host>\S+)\s+(?P<process>\S+):\s+(?P<message>.*)'
)

KEYVALUE_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}).*?'
    r'user=(?P<user>\S+).*?ip=(?P<ip>\S+).*?status=(?P<status>\S+)'
)

# ---------------------------------------------------------
# FIELD MAPPING HELPERS
# ---------------------------------------------------------

def get_sample_lines(filepath, limit=5):
    lines = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
            if len(lines) >= limit:
                break
    return lines

def guess_fields_from_sample(line):
    parts = line.split()
    return parts, parts

def parse_line_with_mapping(line, logfile_id, mapping):
    parts = line.split()
    if not parts:
        return None

    def get(idx):
        try:
            idx = int(idx)
            return parts[idx] if 0 <= idx < len(parts) else None
        except:
            return None

    return LogEntry(
        timestamp=get(mapping.get("timestamp_index")),
        username=get(mapping.get("username_index")),
        ip_address=get(mapping.get("ip_index")),
        status=get(mapping.get("status_index")),
        raw_line=line,
        logfile_id=logfile_id
    )

def parse_with_mapping(filepath, logfile_id, mapping):
    count = 0
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = parse_line_with_mapping(line, logfile_id, mapping)
            if entry:
                db.session.add(entry)
                count += 1
    db.session.commit()
    return count

# ---------------------------------------------------------
# AUTO-DETECT PARSERS
# ---------------------------------------------------------

def detect_log_type(line):
    if APACHE_PATTERN.match(line): return "apache"
    if SSH_PATTERN.match(line): return "ssh"
    if SYSLOG_PATTERN.match(line): return "syslog"
    if KEYVALUE_PATTERN.match(line): return "keyvalue"
    return "generic"

def parse_apache(line, logfile_id):
    m = APACHE_PATTERN.match(line)
    if not m: return None
    return LogEntry(
        timestamp=m.group("timestamp"),
        username=None if m.group("user") == "-" else m.group("user"),
        ip_address=m.group("ip"),
        status=m.group("status"),
        raw_line=line,
        logfile_id=logfile_id
    )

def parse_ssh(line, logfile_id):
    m = SSH_PATTERN.match(line)
    if not m: return None
    return LogEntry(
        timestamp=m.group("timestamp"),
        username=None,
        ip_address=m.group("ip"),
        status="SSH",
        raw_line=line,
        logfile_id=logfile_id
    )

def parse_syslog(line, logfile_id):
    m = SYSLOG_PATTERN.match(line)
    if not m: return None
    return LogEntry(
        timestamp=m.group("timestamp"),
        username=None,
        ip_address=None,
        status=m.group("process"),
        raw_line=line,
        logfile_id=logfile_id
    )

def parse_keyvalue(line, logfile_id):
    m = KEYVALUE_PATTERN.match(line)
    if not m: return None
    return LogEntry(
        timestamp=m.group("timestamp"),
        username=m.group("user"),
        ip_address=m.group("ip"),
        status=m.group("status"),
        raw_line=line,
        logfile_id=logfile_id
    )

def parse_generic(line, logfile_id):
    parts = line.split()
    if not parts: return None
    return LogEntry(
        timestamp=parts[0],
        username=None,
        ip_address=None,
        status=None,
        raw_line=line,
        logfile_id=logfile_id
    )

# ---------------------------------------------------------
# UNIVERSAL PARSER
# ---------------------------------------------------------

def parse_universal(filepath, logfile_id):
    count = 0
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            t = detect_log_type(line)

            if t == "apache": entry = parse_apache(line, logfile_id)
            elif t == "ssh": entry = parse_ssh(line, logfile_id)
            elif t == "syslog": entry = parse_syslog(line, logfile_id)
            elif t == "keyvalue": entry = parse_keyvalue(line, logfile_id)
            else: entry = parse_generic(line, logfile_id)

            if entry:
                db.session.add(entry)
                count += 1

    db.session.commit()
    return count

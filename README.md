# 🔐 LogSentinel  
**Web-Based Log Analysis Platform for Small Businesses**

LogSentinel is a lightweight, web-based log analysis platform designed to help small businesses monitor server and authentication logs, detect suspicious activity, and visualize security-relevant patterns without requiring advanced cybersecurity expertise.

The system focuses on accessibility, transparency, and ease of use, enabling users to upload log files, analyze them for anomalies, and review results through an intuitive dashboard.

---

## 📌 Features

- 📂 Upload and analyze server or authentication log files
- 🔍 Rule-based anomaly detection (e.g., failed login attempts, suspicious IPs)
- 📊 Interactive dashboard with visual summaries
- 🧠 Transparent and interpretable detection logic
- 🌐 Web-based interface

---

## 🏗️ System Architecture

LogSentinel follows a modular, client–server architecture:

- **Web User Interface** – User interaction and visualization
- **Backend Controller (Flask)** – Request handling and coordination
- **Log Parsing Module** – Validation and normalization of log data
- **Anomaly Detection Module** – Rule-based detection of suspicious patterns
- **Database (SQLite)** – Persistent storage of logs and analysis results
- **Dashboard / Visualization** – Charts and summary metrics

UML component and sequence diagrams are included in the project documentation.

---

## 🧪 Testing

The system has been tested using predefined test cases, including:

- Logs with repeated failed login attempts
- Logs with normal authentication behavior
- Empty or invalid log files
- Mixed successful and failed login scenarios



---

## 🛠️ Technology Stack

| Component | Technology |
|---------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python (Flask) |
| Database | SQLite |
| Visualization | JavaScript chart libraries |
| Architecture | Client–Server |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- pip

### Installation
```bash
git clone https://github.com/your-username/logsentinel.git
cd logsentinel
pip install -r requirements.txt
```

### Run the Application
```
python run.py

```




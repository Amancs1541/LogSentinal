from flask import Blueprint, jsonify
import requests

geo_bp = Blueprint("geo", __name__)

@geo_bp.route("/geo/<ip>")
def geo_lookup(ip):
    # Private IP check
    private_ranges = ("192.168.", "10.", "172.16.")
    if ip.startswith(private_ranges):
        return jsonify({"city": None, "country": "Private Network"})

    try:
        res = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
        data = res.json()
        return jsonify({
            "city": data.get("city"),
            "country": data.get("country_name")
        })
    except:
        return jsonify({"city": None, "country": "Unknown"})

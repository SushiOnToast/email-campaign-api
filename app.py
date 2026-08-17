import os
from datetime import datetime
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from dotenv import dotenv_values

import config
from classification.classifier import run_classification
from outreach.gmail_sender import send_campaign
from outreach.email_templates import DEFAULT_SUBJECT_TEMPLATE, DEFAULT_BODY_TEMPLATE

from main import run_discovery

app = Flask(__name__)
app.secret_key = "hello1234"

ENV_PATH = ".env"


def get_attachment_filename():
    if os.path.exists(config.PRESENTATION_PATH):
        return os.path.basename(config.PRESENTATION_PATH)
    return None


def get_dashboard_stats():
    total_buyers = 0
    sent_count = 0
    failed_count = 0

    if os.path.exists(config.BUYERS_CSV):
        df = pd.read_csv(config.BUYERS_CSV)
        total_buyers = len(df)

    if os.path.exists(config.SENT_LOG_CSV):
        log = pd.read_csv(config.SENT_LOG_CSV)
        if "status" in log.columns:
            sent_count = int((log["status"] == "sent").sum())
            failed_count = int((log["status"] == "failed").sum())

    return {
        "total_buyers": total_buyers,
        "sent_count": sent_count,
        "failed_count": failed_count,
    }


def get_upload_stats():
    if not os.path.exists(config.BUYERS_CSV):
        return {"row_count": 0, "file_size": 0, "last_modified": None, "buyer_rows": []}

    df = pd.read_csv(config.BUYERS_CSV)
    df = df.fillna("")  # avoid literal "nan" showing up in the template for empty cells
    row_count = len(df)
    file_size = os.path.getsize(config.BUYERS_CSV)
    last_modified_ts = os.path.getmtime(config.BUYERS_CSV)
    last_modified = datetime.fromtimestamp(last_modified_ts).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "row_count": row_count,
        "file_size": file_size,
        "last_modified": last_modified,
        "buyer_rows": df.to_dict("records"),
    }


def get_report_stats():
    if not os.path.exists(config.SENT_LOG_CSV):
        return {
            "total_sent": 0,
            "success_count": 0,
            "failed_count": 0,
            "success_rate": 0,
            "log_rows": [],
        }

    df = pd.read_csv(config.SENT_LOG_CSV)
    df = df.fillna("")  # same fix here in case any log rows have blank fields
    total_sent = len(df)
    success_count = int((df["status"] == "sent").sum()) if "status" in df.columns else 0
    failed_count = int((df["status"] == "failed").sum()) if "status" in df.columns else 0
    success_rate = round((success_count / total_sent) * 100, 1) if total_sent > 0 else 0

    return {
        "total_sent": total_sent,
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": success_rate,
        "log_rows": df.to_dict("records"),
    }


def read_env_settings():
    """
    Reads current values fresh from the .env file on disk (not from
    config's cached module-level variables), so the settings page
    always reflects the latest saved values without needing an app restart.
    """
    env_values = dotenv_values(ENV_PATH)

    return {
        "gmail_email": env_values.get("GMAIL_EMAIL", config.GMAIL_EMAIL),
        "search_keyword": env_values.get("SEARCH_KEYWORD", config.SEARCH_KEYWORD),
        "send_delay": env_values.get("SEND_DELAY_SECONDS", config.SEND_DELAY_SECONDS),
        "daily_send_limit": env_values.get("DAILY_SEND_LIMIT", config.DAILY_SEND_LIMIT),
    }


def write_env_settings(updates: dict):
    current_lines = {}

    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                current_lines[key.strip()] = value.strip()

    for key, value in updates.items():
        if value is not None and value != "":
            current_lines[key] = value

    with open(ENV_PATH, "w") as f:
        for key, value in current_lines.items():
            f.write(f"{key}={value}\n")


@app.route("/")
def dashboard():
    stats = get_dashboard_stats()
    return render_template("dashboard.html", **stats)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        uploaded_file = request.files.get("csv_file")
        if uploaded_file and uploaded_file.filename.endswith(".csv"):
            os.makedirs(config.DATA_DIR, exist_ok=True)
            uploaded_file.save(config.BUYERS_CSV)
            flash("CSV uploaded successfully.")
        return redirect(url_for("upload"))

    stats = get_upload_stats()
    return render_template("upload.html", **stats)


@app.route("/run-discovery", methods=["POST"])
def run_discovery_route():
    try:
        new_buyers = run_discovery()
        flash(f"Discovery complete — {len(new_buyers)} new buyer(s) found.")
    except Exception as e:
        flash(f"Discovery failed: {e}")
    return redirect(url_for("upload"))


@app.route("/classify", methods=["GET", "POST"])
def classify():
    result = None
    if request.method == "POST":
        result = run_classification()
    return render_template("classify.html", result=result)


@app.route("/send", methods=["GET", "POST"])
def send():
    result = None

    if request.method == "POST":
        uploaded_presentation = request.files.get("presentation_file")
        if uploaded_presentation and uploaded_presentation.filename:
            os.makedirs(os.path.dirname(config.PRESENTATION_PATH) or ".", exist_ok=True)
            uploaded_presentation.save(config.PRESENTATION_PATH)
            flash(f"Presentation updated: {uploaded_presentation.filename}")

        subject = request.form.get("subject")
        body = request.form.get("body")
        audience = request.form.get("audience")
        result = send_campaign(subject, body, audience)

    return render_template(
        "send.html",
        result=result,
        default_subject=DEFAULT_SUBJECT_TEMPLATE,
        default_body=DEFAULT_BODY_TEMPLATE,
        attachment_filename=get_attachment_filename(),
    )


@app.route("/report")
def report():
    stats = get_report_stats()
    return render_template("report.html", **stats)


@app.route("/download-report")
def download_report():
    if not os.path.exists(config.SENT_LOG_CSV):
        return "No report available yet", 404
    return send_file(config.SENT_LOG_CSV, as_attachment=True, download_name="campaign_report.csv")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    message = None
    if request.method == "POST":
        updates = {
            "SEARCH_KEYWORD": request.form.get("search_keyword"),
            "SEND_DELAY_SECONDS": request.form.get("send_delay"),
            "DAILY_SEND_LIMIT": request.form.get("daily_send_limit"),
        }
        write_env_settings(updates)
        message = "Settings saved. Restart the app for changes to take effect."

    current = read_env_settings()
    return render_template("settings.html", message=message, **current)


if __name__ == "__main__":
    app.run(debug=True)
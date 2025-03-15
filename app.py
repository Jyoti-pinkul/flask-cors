import io
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from models import db, Record
from config import SQLALCHEMY_DATABASE_URI
from datetime import datetime, timedelta, date

app = Flask(__name__)
CORS(app, resources={r"/get": {"origins": "*"}, r"/chart": {"origins": "*"}})  # Enable CORS for API

# Database Config
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chart")
def generate_chart():
    filter_type = request.args.get("filter", "overall")
    today = date.today()

    if filter_type == "hour":
        start_time = datetime.utcnow() - timedelta(hours=1)
    elif filter_type == "today":
        start_time = datetime.combine(today, datetime.min.time())
    elif filter_type == "previous_day":
        previous_day = today - timedelta(days=1)
        start_time = datetime.combine(previous_day, datetime.min.time())
    else:
        start_time = None

    query = db.session.query(Record)
    if start_time:
        query = query.filter(Record.created_at >= start_time)

    records = query.all()

    labels = []
    counts = []
    if filter_type in ["today", "previous_day"]:
        hours = [f"{h}:00" for h in range(24)]
        counts = [0] * 24
        for record in records:
            hour = record.created_at.hour
            counts[hour] += 1
        labels = hours
    else:
        days = [(today - timedelta(days=i)) for i in range(7)]
        counts = [db.session.query(Record).filter(
            Record.created_at >= d, Record.created_at < d + timedelta(days=1)).count() for d in days]
        labels = [d.strftime("%Y-%m-%d") for d in days]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, counts, color="skyblue")
    plt.xlabel("Time")
    plt.ylabel("Records Added")
    plt.title(f"Records Count ({filter_type.capitalize()})")
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

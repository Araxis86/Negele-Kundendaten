
from flask import Flask, request, render_template
import smtplib
from email.message import EmailMessage
import io
import csv
import base64
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = {
        "Vorname": request.form["vorname"],
        "Nachname": request.form["nachname"],
        "Anschrift": request.form["anschrift_strasse"] + ", " + request.form["anschrift_plz_ort"],
        "Lieferanschrift": request.form["liefer_strasse"] + ", " + request.form["liefer_plz_ort"],
        "Stockwerk": request.form["stockwerk"],
        "Aufzug": request.form["aufzug_vorhanden"],
        "Telefon": request.form["telefon"],
        "Handy": request.form["handy"],
        "Email1": request.form["email"],
        "Email2": request.form["email2"],
        "Quelle": request.form["quelle"],
        "Berater": request.form["berater"]
    }

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(data.keys())
    writer.writerow(data.values())

    msg = EmailMessage()
    msg["Subject"] = f"Neue Kundendaten von {data['Vorname']} {data['Nachname']}"
    msg["From"] = os.environ.get("SMTP_USER")
    msg["To"] = data["Berater"] or "info@negele.com"
    msg.set_content("Im Anhang finden Sie die Kundendaten als CSV-Datei und die Unterschrift.")

    msg.add_attachment(csv_buffer.getvalue(), filename="kundendaten.csv", subtype="csv", maintype="text")

    signature_data = request.form.get('signature_data')
    if signature_data:
        encoded_image = signature_data.split(",")[1]
        signature_bytes = base64.b64decode(encoded_image)
        msg.add_attachment(signature_bytes, maintype="image", subtype="png", filename="unterschrift.png")

    smtp_server = os.environ.get("SMTP_SERVER", "smtp.web.de")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")

    with smtplib.SMTP_SSL(smtp_server, 465) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

    return "Vielen Dank – die Daten wurden per E-Mail versendet."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

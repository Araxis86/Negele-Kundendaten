
from flask import Flask, request, render_template
import smtplib
from email.message import EmailMessage
import io
import csv

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
    msg["From"] = "formular@negele.com"
    msg["To"] = data["Berater"]
    msg.set_content("Im Anhang finden Sie die Kundendaten als CSV-Datei.")
    msg.add_attachment(csv_buffer.getvalue(), filename="kundendaten.csv", subtype="csv", maintype="text")
    import base64
    signature_data = request.form.get('signature_data')
    if signature_data:
        encoded_image = signature_data.split(",")[1]
        signature_bytes = base64.b64decode(encoded_image)
        msg.add_attachment(signature_bytes, maintype="image", subtype="png", filename="unterschrift.png")


    with smtplib.SMTP_SSL("smtp.example.com", 465) as smtp:
        smtp.login("formular@negele.com", "DEIN_PASSWORT")
        smtp.send_message(msg)

    return "Vielen Dank – die Daten wurden per E-Mail versendet."

if __name__ == "__main__":
    app.run(debug=True)

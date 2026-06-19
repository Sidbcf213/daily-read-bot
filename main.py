import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

app = Flask(__name__)

TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_WHATSAPP = "whatsapp:+14155238886"
YOUR_WHATSAPP = "whatsapp:+9647887804163"
genai.configure(api_key=os.environ.get("GEMINI_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

def get_daily_read():
    today = datetime.date.today().strftime("%A %d %B %Y")
    return ask_gemini(f"Today is {today}. Generate a 150-word daily read for an Algerian math teacher interested in: halal stock investing, e-commerce for beginners, English improvement, or math teaching tips. Pick one topic randomly. Start with an emoji and topic name, then a title, then content. Be practical.")

def send_daily_read():
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(body=get_daily_read(), from_=TWILIO_WHATSAPP, to=YOUR_WHATSAPP)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming = request.form.get("Body", "").strip()
    resp = MessagingResponse()
    if incoming.lower() in ["hi", "hello", "read", "send"]:
        resp.message(get_daily_read())
    else:
        reply = ask_gemini(f"An Algerian math teacher asks: '{incoming}'. Answer briefly in simple English. Topics: halal investing, e-commerce, English learning, math teaching.")
        resp.message(reply)
    return str(resp)

@app.route("/")
def home():
    return "Bot is running!"

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_read, "cron", hour=7, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

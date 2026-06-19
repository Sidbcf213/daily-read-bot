import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import anthropic
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

app = Flask(__name__)

TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_WHATSAPP = "whatsapp:+14155238886"
YOUR_WHATSAPP = "whatsapp:+9647887804163"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

def get_daily_read():
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    today = datetime.date.today().strftime("%A %d %B %Y")
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": f"Today is {today}. Generate a 150-word daily read for an Algerian math teacher interested in: halal stock investing (Algeria, Saudi, global markets), e-commerce for beginners, English improvement, or math teaching tips. Pick one topic randomly. Format: start with an emoji and topic name on line 1, then a title, then the content. Be practical and concise."}]
    )
    return msg.content[0].text

def send_daily_read():
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    text = get_daily_read()
    client.messages.create(body=text, from_=TWILIO_WHATSAPP, to=YOUR_WHATSAPP)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming = request.form.get("Body", "").strip().lower()
    resp = MessagingResponse()
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    
    if incoming in ["hi", "hello", "read", "send"]:
        text = get_daily_read()
        resp.message(text)
    else:
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": f"An Algerian math teacher asks: '{incoming}'. Answer briefly in simple English. Topics: halal investing, e-commerce, English learning, math teaching."}]
        )
        resp.message(reply.content[0].text)
    return str(resp)

@app.route("/")
def home():
    return "Bot is running!"

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_read, "cron", hour=7, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

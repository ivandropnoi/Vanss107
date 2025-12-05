import os
import telebot
import requests
import json
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# ==== AI FUNCTION ====
def ask_ai(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

# ==== HANDLE TEXT ====
@bot.message_handler(func=lambda m: True)
def reply(message):
    bot.send_chat_action(message.chat.id, "typing")
    try:
        ai = ask_ai(message.text)
        bot.send_message(message.chat.id, ai)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# ==== WEBHOOK (REQUIRED FOR HOSTING) ====
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_URL") + TELEGRAM_TOKEN)
    return "Bot active!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
  

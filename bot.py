import os
import telebot
from telebot import types

# ከ @BotFather የሚቀበሉትን ቶክን እዚህ ያስገቡ (ወይም በሰርቨር ላይ Environment Variable አድርገው ይጫኑት)
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# የተጠቃሚዎችን የቀን ፍለጋ ብዛት ለመቆጣጠር (User ID -> Search Count)
user_search_counts = {}
DAILY_LIMIT = 5

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"ሰላም {user_name}! 🤖\nእኔ የዩቲዩብ ቪዲዮ መፈለጊያ ቦት ነኝ።\nለመፈለግ የሚፈልጉትን ቃል ይጻፉ (በቀን እስከ {DAILY_LIMIT} ጊዜ በነፃ መፈለግ ይችላሉ)።")

@bot.message_handler(func=lambda message: True)
def search_youtube(message):
    user_id = message.from_user.id
    query = message.text.strip()

    # የቀን ገደብ ማረጋገጫ (Rate Limiting)
    current_count = user_search_counts.get(user_id, 0)
    if current_count >= DAILY_LIMIT:
        bot.reply_to(message, "⚠️ ይቅርታ! የዛሬውን የነፃ ፍለጋ ገደብ (5/5) ጨርሰዋል ነገ እንደገና ይሞክሩ።")
        return

    # ብዛቱን በአንድ እንጨምራለን
    user_search_counts[user_id] = current_count + 1
    remaining = DAILY_LIMIT - (current_count + 1)

    # የፍለጋ ውጤቱን እና የዩቲዩብ ሊንክ እንልካለን
    bot.reply_to(message, f"🔍 እየፈለኩ ነው: '{query}'...\n\n🔗 የዩቲዩብ ሊክ: https://www.youtube.com/results?search_query={query.replace(' ', '+')}\n\n📊 የቀረዎ ነፃ ፍለጋ: {remaining} ከ {DAILY_LIMIT}")

if __name__ == "__main__":
    print("ቦቱ እየሰራ ነው...")
    bot.infinity_polling()
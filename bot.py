import os
import telebot
from telebot import types

# ከ @BotFather የሚቀበሉትን ቶክን ከሰርቨር (Railway) Environment Variable (BOT_TOKEN) ይወስዳል
TOKEN = os.getenv("BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"ሰላም {user_name}! 🤖\nእኔ የዩቲዩብ ቪዲዮ መፈለጊያ እና ልዩ ሊንክ አቅራቢ ቦት ነኝ።\nየፈለጉትን ቃል መጻፍ ወይም የተለዩ ቃላትን በመጻፍ የሚፈልጉትን ሊንክ ማግኘት ይችላሉ!")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.strip().lower()
    
    # 1. ተጠቃሚው "afila fikr" ብሎ ከጻፈ የሚሰጠው ልዩ ምላሽ
    if "afila fikr" in text:
        custom_link = "https://www.youtube.com/results?search_query=afila+fikr" # የሚፈልጉትን ትክክለኛ ሊንክ እዚህ መቀየር ይችላሉ
        bot.reply_to(message, f"📚 ለጠየቁት 'Afila Fikr' የተዘጋጀው ሊንክ ይህ ነው:\n\n🔗 {custom_link}")
    
    # 2. ተጠቃሚው ሌላ ማንኛውም ሊንክ ከላከ
    elif "http://" in text or "https://" in text:
        bot.reply_to(message, f"🔗 ሊንክዎ ደርሶኛል!\n\nተቀብዬዋለሁ: {message.text}")
    
    # 3. ሌላ ሳራማ ቃል ከጻፈ የተለመደውን የዩቲዩብ ፍለጋ ይሰራል
    else:
        query = message.text.strip()
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        bot.reply_to(message, f"🔍 እየፈለኩ ነው: '{query}'...\n\n🔗 የዩቲዩብ ሊንክ: {search_url}")

if __name__ == "__main__":
    print("ቦቱ እየሰራ ነው...")
    bot.infinity_polling()

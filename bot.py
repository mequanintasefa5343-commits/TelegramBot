import os
import telebot
from telebot import types
from duckduckgo_search import DDGS

TOKEN = os.getenv("BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)

# የተጠቃሚዎች የቋንቋ ምርጫ ማከማቻ (Default: English/Amharic mix)
user_lang = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔍 Search Exam/Web"),
        types.KeyboardButton("❓ Help / እገዛ"),
        types.KeyboardButton("🌐 Change Language (Amharic/English)")
    )
    bot.reply_to(
        message, 
        f"ሰላም {user_name}! 🤖\nእኔ የትምህርት፣ የፈተና እና የዌብሳይት ሊንክ መፈለጊያ ቦት ነኝ። የሚፈልጉትን ርዕስ በቀጥታ ይጻፉልኝ!",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "🤖 **የቦቱ አጠቃቀም መመሪያ:**\n\n"
        "1️⃣ **ፍለጋ ለማድረግ:** ማንኛውንም የትምህርት ርዕስ፣ የፈተና ጥያቄ (Exam) ወይም ቃል በቀጥታ ይጻፉ።\n"
        "2️⃣ **ሊንኮች:** ቦቱ የጉግል እና የዩቲዩብ ቀጥተኛ የፍለጋ ሊንኮችን ያዘጋጅልዎታል።\n"
        "3️⃣ **ትዕዛዞች:**\n"
        "   - /start - ቦቱን እንደገና ለመጀመር\n"
        "   - /help - ይህንን የረዳት መመሪያ ለማግኘት"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.strip()
    text_lower = text.lower()
    
    if text_lower in ["❓ help / እገዛ", "/help"]:
        send_help(message)
        return
        
    if text_lower in ["🌐 change language (amharic/english)", "language"]:
        chat_id = message.chat.id
        current = user_lang.get(chat_id, "am")
        if current == "am":
            user_lang[chat_id] = "en"
            bot.reply_to(message, "🌐 Language switched to English. Send any query to search!")
        else:
            user_lang[chat_id] = "am"
            bot.reply_to(message, "🌐 ቋንቋ ወደ አማርኛ ተቀይሯል። የሚፈልጉትን ርዕስ ይጻፉ!")
        return

    if "afila fikr" in text_lower:
        custom_link = "https://www.youtube.com/results?search_query=afila+fikr"
        bot.reply_to(message, f"📚 ለጠየቁት 'Afila Fikr' የተዘጋጀው ሊንክ ይህ ነው:\n\n🔗 {custom_link}")
        return
    
    if "http://" in text_lower or "https://" in text_lower:
        bot.reply_to(message, f"🔗 ሊንክዎ ደርሶኛል!\n\nተቀብዬዋለሁ: {text}")
        return
    
    # የፍለጋ ሂደት
    bot.reply_to(message, f"🔍 '{text}' በመፈለግ ላይ...")
    
    results = []
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(text, max_results=3))
            if search_results:
                results = search_results
    except Exception as e:
        print(f"Search Error: {e}")
        
    google_url = f"https://www.google.com/search?q={text.replace(' ', '+')}"
    yt_url = f"https://www.youtube.com/results?search_query={text.replace(' ', '+')}"
    
    response_text = f"🌐 **ለ '{text}' የተገኙ የፍለጋ ሊንኮች:**\n\n"
    
    if results:
        for item in results:
            title = item.get('title', 'ርዕስ የለውም')
            href = item.get('href', '#')
            response_text += f"📌 **{title}**\n🔗 {href}\n\n"
    
    response_text += f"📌 **ጉግል ፍለጋ ሊንክ:**\n{google_url}\n\n📌 **ዩቲዩብ ፍለጋ ሊንክ:**\n{yt_url}"
    
    bot.send_message(message.chat.id, response_text, disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()

import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types
from duckduckgo_search import DDGS

# --- RENDER PORT BINDING FIX (KEEP-ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ---------------------------------------------

TOKEN = os.getenv("BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)

user_history = {}
user_favorites = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔬 Pathology Exams"),
        types.KeyboardButton("🦴 Anatomy Notes"),
        types.KeyboardButton("🧠 Physiology PDFs"),
        types.KeyboardButton("📂 PDF Files Filter"),
        types.KeyboardButton("⭐ My Favorites"),
        types.KeyboardButton("📜 Search History"),
        types.KeyboardButton("❓ Help / እገዛ")
    )
    
    bot.reply_to(
        message, 
        f"ሰላም {user_name}! 🤖\nእኔ የህክምና ትምህርት፣ የፈተና እና የፒዲኤፍ ዌብሳይት መፈለጊያ የላቀ ቦት ነኝ። ከታች ካሉት ምድቦች አንዱን ይምረጡ ወይም የሚፈልጉትን ርዕስ በቀጥታ ይጻፉልኝ!",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "🤖 **የቦቱ አጠቃቀም መመሪያ:**\n\n"
        "1️⃣ **የምድብ አዝራሮች:** እንደ Pathology, Anatomy እና Physiology ያሉ የፈተና ኖቶችን በአንድ ክሊክ ለማግኘት።\n"
        "2️⃣ **PDF Files Filter:** ቀጥተኛ የፒዲኤፍ ዶክመንቶችን ብቻ ለማጣራት።\n"
        "3️⃣ **⭐ My Favorites:** ያስቀመጧቸውን ጠቃሚ ሊንኮች ለማየት።\n"
        "4️⃣ **Inline Search:** በየትኛውም ግሩፕ ውስጥ ሆነው `@dersolignbot keyword` ብለው በመጻፍ በቀጥታ ውጤት ማጋራት ይችላሉ።"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.inline_handler(func=lambda query: True)
def inline_search(query):
    text = query.query.strip()
    if not text:
        text = "Medical model exams PDF"
    
    results = []
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(text, max_results=5))
            for i, item in enumerate(search_results):
                title = item.get('title', 'ርዕስ የለውም')
                href = item.get('href', '#')
                snippet = item.get('body', 'ተጨማሪ መረጃ ለማግኘት ሊንኩን ይጫኑ።')
                
                results.append(
                    types.InlineQueryResultArticle(
                        id=str(i),
                        title=title,
                        description=snippet[:100],
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"📌 **{title}**\n🔗 {href}"
                        )
                    )
                )
    except Exception as e:
        print(f"Inline Search Error: {e}")
        
    bot.answer_inline_query(query.id, results, cache_time=1)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.strip()
    text_lower = text.lower()
    chat_id = message.chat.id
    
    if text_lower in ["❓ help / እገዛ", "/help"]:
        send_help(message)
        return
        
    if text_lower == "📜 search history":
        history = user_history.get(chat_id, [])
        if history:
            history_text = "📜 **የመጨረሻ የፍለጋ ታሪክዎ:**\n\n" + "\n".join([f"• {item}" for item in history])
            bot.reply_to(message, history_text)
        else:
            bot.reply_to(message, "📜 እስካሁን የፈለጉት የተመዘገበ ታሪክ የለም።")
        return

    if text_lower == "⭐ my favorites":
        favorites = user_favorites.get(chat_id, [])
        if favorites:
            fav_text = "⭐ **የተቀመጡ ተወዳጅ ሊንኮችዎ:**\n\n" + "\n".join([f"🔗 {item}" for item in favorites])
            bot.reply_to(message, fav_text, disable_web_page_preview=True)
        else:
            bot.reply_to(message, "⭐ እስካሁን ያስቀመጡት ተወዳጅ ሊንክ የለም።")
        return

    if "pathology" in text_lower:
        text = "Pathology exam papers filetype:pdf"
    elif "anatomy" in text_lower:
        text = "Human anatomy notes filetype:pdf"
    elif "physiology" in text_lower:
        text = "Medical physiology exam questions filetype:pdf"
    elif "pdf" in text_lower or "📂 pdf files filter" in text_lower:
        text = "Medical model exams and lecture notes filetype:pdf"

    if chat_id not in user_history:
        user_history[chat_id] = []
    if text not in user_history[chat_id]:
        user_history[chat_id].insert(0, text)
        if len(user_history[chat_id]) > 5:
            user_history[chat_id].pop()

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
    
    response_text = f"🌐 **ለ '{text}' የተገኙ የፍለጋ እና የፒዲኤፍ ሊንኮች:**\n\n"
    
    if results:
        for item in results:
            title = item.get('title', 'ርዕስ የለውም')
            href = item.get('href', '#')
            response_text += f"📌 **{title}**\n🔗 {href}\n\n"
    
    response_text += f"📌 **ጉግል እና ፒዲኤፍ ፍለጋ:**\n{google_url}\n\n📌 **ዩቲዩብ የቪዲዮ ሊንክ:**\n{yt_url}"
    
    if "http://" in text_lower or "https://" in text_lower:
        if chat_id not in user_favorites:
            user_favorites[chat_id] = []
        if text not in user_favorites[chat_id]:
            user_favorites[chat_id].append(text)
        bot.reply_to(message, "⭐ ሊንኩ በተወዳጆችዎ (Favorites) ዝርዝር ውስጥ ተቀምጧል!")
        return

    bot.send_message(message.chat.id, response_text, disable_web_page_preview=True)

if __name__ == "__main__":
    # ዌብ ሰርቨሩን በጀርባ ማስነሳት
    keep_alive()
    # የቦቱን ፖሊንግ ማስጀመር
    bot.infinity_polling(none_stop=True)

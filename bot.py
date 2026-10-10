import os
import telebot
from telebot import types
from duckduckgo_search import DDGS

TOKEN = os.getenv("BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)

# የተጠቃሚዎች መረጃ እና የፍለጋ ታሪክ ማከማቻ (History)
user_history = {}
user_lang = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    # ዋና ዋና የምድብ አዝራሮች (Category Buttons)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔬 Pathology Exams"),
        types.KeyboardButton("🦴 Anatomy Notes"),
        types.KeyboardButton("🧠 Physiology PDFs"),
        types.KeyboardButton("📚 General Search"),
        types.KeyboardButton("📜 Search History"),
        types.KeyboardButton("❓ Help / እገዛ")
    )
    
    bot.reply_to(
        message, 
        f"ሰላም {user_name}! 🤖\nእኔ የህክምና ትምህርት፣ የፈተና 资料 እና የዌብሳይት ሊንክ መፈለጊያ የላቀ ቦት ነኝ። ከታች ካሉት ምድቦች አንዱን ይምረጡ ወይም የሚፈልጉትን ርዕስ በቀጥታ ይጻፉልኝ!",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "🤖 **የቦቱ አጠቃቀም መመሪያ:**\n\n"
        "1️⃣ **የምድብ አዝራሮች:** እንደ Pathology, Anatomy እና Physiology ያሉ ፈጣን ርዕሶችን በአዝራር ይምረጡ።\n"
        "2️⃣ **የፍለጋ ታሪክ (History):** የፈለጓቸውን ርዕሶች ለማየት '📜 Search History' የሚለውን ይጫኑ።\n"
        "3️⃣ **ቀጥተኛ ፍለጋ:** ማንኛውንም የፈተና ቃል በቀጥታ በመጻፍ የጉግል እና የዩቲዩብ ሊንኮችን ያግኙ።\n"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

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

    # የምድብ አቋራጮች (Category Shortcuts)
    if "pathology" in text_lower:
        text = "Pathology exam papers and model questions PDF"
    elif "anatomy" in text_lower:
        text = "Human anatomy upper limb and clinical anatomy notes"
    elif "physiology" in text_lower:
        text = "Medical physiology exam questions and summaries"

    # የፍለጋ ታሪክን ማስቀመጥ (최신 5 queries)
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
    
    response_text = f"🌐 **ለ '{text}' የተገኙ የፍለጋ ሊንኮች:**\n\n"
    
    if results:
        for item in results:
            title = item.get('title', 'ርዕስ የለውም')
            href = item.get('href', '#')
            response_text += f"📌 **{title}**\n🔗 {href}\n\n"
    
    response_text += f"📌 **ጉግል ፍለጋ እና ፒዲኤፍ ሊንክ:**\n{google_url}\n\n📌 **ዩቲዩብ የቪዲዮ ሊንክ:**\n{yt_url}"
    
    bot.send_message(message.chat.id, response_text, disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()

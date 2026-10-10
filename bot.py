import os
import telebot
from telebot import types
from duckduckgo_search import DDGS

# የቦት ቶክን ከሰርቨር Environment Variable መቀበያ
TOKEN = os.getenv("BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"ሰላም {user_name}! 🤖\nእኔ የቪዲዮ፣ የትምህርት፣ የፈተና (Exam) እና የዌብሳይት ሊንክ መፈለጊያ ቦት ነኝ።\nየሚፈልጉትን ቃል በመጻፍ ፍለጋ ማካሄድ ይችላሉ!")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.strip()
    text_lower = text.lower()
    
    # 1. ተጠቃሚው "afila fikr" ብሎ ከጻፈ የሚሰጠው ልዩ ምላሽ
    if "afila fikr" in text_lower:
        custom_link = "https://www.youtube.com/results?search_query=afila+fikr"
        bot.reply_to(message, f"📚 ለጠየቁት 'Afila Fikr' የተዘጋጀው ሊንክ ይህ ነው:\n\n🔗 {custom_link}")
    
    # 2. ተጠቃሚው ቀጥታ ሊንክ ከላከ
    elif "http://" in text_lower or "https://" in text_lower:
        bot.reply_to(message, f"🔗 ሊንክዎ ደርሶኛል!\n\nተቀብዬዋለሁ: {text}")
    
    # 3. ማንኛውንም ትምህርት፣ ፈተና (Exam) ወይም የዌብሳይት ሊንክ በነፃ መፈለጊያ
    else:
        bot.reply_to(message, f"🔍 '{text}' በመፈለግ ላይ...")
        
        try:
            results = []
            # DuckDuckGo በመጠቀም የዌብሳይት ሊንኮችን መፈለግ
            with DDGS() as ddgs:
                for r in ddgs.text(text, max_results=3):
                    results.append(r)
            
            if results:
                response_text = f"🌐 **ለ '{text}' የተገኙ የዌብ እና የፈተና ሊንኮች:**\n\n"
                for item in results:
                    response_text += f"📌 **{item['title']}**\n🔗 {item['href']}\n\n"
            else:
                # የዌብ ውጤት ካልተገኘ ወደ ዩቲዩብ ፍለጋ መቀየር
                yt_url = f"https://www.youtube.com/results?search_query={text.replace(' ', '+')}"
                response_text = f"🔗 **የዩቲዩብ ፍለጋ ሊንክ:**\n{yt_url}"
                
            bot.send_message(message.chat.id, response_text, disable_web_page_preview=True)
            
        except Exception as e:
            # ችግር ሲፈጠር ወደ ዩቲዩብ ሊንክ መላክ
            yt_url = f"https://www.youtube.com/results?search_query={text.replace(' ', '+')}"
            bot.reply_to(message, f"🔗 **የዩቲዩብ ፍለጋ ሊንክ:**\n{yt_url}")

if __name__ == "__main__":
    print("ቦቱ እየሰራ ነው...")
    bot.infinity_polling()

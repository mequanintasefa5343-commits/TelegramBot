import os
import telebot
from telebot import types
from duckduckgo_search import DDGS

TOKEN = os.getenv("BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"ሰላም {user_name}! 🤖\nእኔ የቪዲዮ፣ የትምህርት፣ የፈተና እና የዌብሳይት ሊንክ መፈለጊያ ቦት ነኝ።")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.strip()
    text_lower = text.lower()
    
    if "afila fikr" in text_lower:
        custom_link = "https://www.youtube.com/results?search_query=afila+fikr"
        bot.reply_to(message, f"📚 ለጠየቁት 'Afila Fikr' የተዘጋጀው ሊንክ ይህ ነው:\n\n🔗 {custom_link}")
    
    elif "http://" in text_lower or "https://" in text_lower:
        bot.reply_to(message, f"🔗 ሊንክዎ ደርሶኛል!\n\nተቀብዬዋለሁ: {text}")
    
    else:
        bot.reply_to(message, f"🔍 '{text}' በመፈለግ ላይ...")
        
        try:
            results = []
            # ትክክለኛውን የ duckduckgo_search አጠቃቀም
            with DDGS() as ddgs:
                for r in ddgs.text(text, max_results=3):
                    results.append(r)
            
            if results:
                response_text = f"🌐 **ለ '{text}' የተገኙ የዌብ እና የፈተና ሊንኮች:**\n\n"
                for item in results:
                    title = item.get('title', 'ርዕስ የለውም')
                    href = item.get('href', '#')
                    response_text += f"📌 **{title}**\n🔗 {href}\n\n"
            else:
                yt_url = f"https://www.youtube.com/results?search_query={text.replace(' ', '+')}"
                response_text = f"🔗 **የዩቲዩብ ፍለጋ ሊንክ:**\n{yt_url}"
                
            bot.send_message(message.chat.id, response_text, disable_web_page_preview=True)
            
        except Exception as e:
            yt_url = f"https://www.youtube.com/results?search_query={text.replace(' ', '+')}"
            bot.reply_to(message, f"🔗 **የዩቲዩብ ፍለጋ ሊንክ:**\n{yt_url}")

if __name__ == "__main__":
    bot.infinity_polling()

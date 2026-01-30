import telebot
import time
from flask import Flask
from threading import Thread

# --- 1. حل مشكلة الـ Port لـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def start_web_server():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. إعداد البوت ---
API_TOKEN = '8346075393:AAF8vUnRtUj2STFR5aBW47Nnctwn08LXp1A'
ADMIN_ID = 7605020034 
UNIT_ID = 'bot-22081'

bot = telebot.TeleBot(API_TOKEN)
users_db = {} # ملاحظة: في Render البيانات ستضيع عند إعادة التشغيل، لاحقاً سنستخدم قاعدة بيانات

def get_u(uid):
    if uid not in users_db: users_db[uid] = 0
    return users_db[uid]

# --- 3. الأوامر والأزرار ---
@bot.message_handler(commands=['start'])
def welcome(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📺 مشاهدة إعلان (+10)', '💰 رصيدي')
    markup.add('🛒 متجر الحسابات', '🎁 جوائز أسبوعية')
    bot.send_message(m.chat.id, "مرحباً بك في بوت الحسابات العالمي! 🚀", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '💰 رصيدي')
def bal(m):
    bot.reply_to(m, f"💎 رصيدك الحالي: {get_u(m.from_user.id)} نقطة")

@bot.message_handler(func=lambda m: m.text == '🛒 متجر الحسابات')
def shop(m):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("🇺🇸 أمريكي (500)", callback_data="buy_us"))
    kb.add(telebot.types.InlineKeyboardButton("🇫🇷 فرنسي (450)", callback_data="buy_fr"))
    kb.add(telebot.types.InlineKeyboardButton("🇯🇵 ياباني (600)", callback_data="buy_jp"))
    bot.send_message(m.chat.id, "اختر الحساب المطلوب:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('buy_'))
def process_buy(c):
    price = {"buy_us": 500, "buy_fr": 450, "buy_jp": 600}[c.data]
    name = {"buy_us": "أمريكي", "buy_fr": "فرنسي", "buy_jp": "ياباني"}[c.data]
    uid = c.from_user.id
    
    if users_db.get(uid, 0) >= price:
        users_db[uid] -= price
        bot.send_message(c.message.chat.id, f"✅ طلبك قيد التنفيذ لحساب {name}. سيصلك الكود هنا قريباً.")
        bot.send_message(ADMIN_ID, f"🚨 طلب جديد: {name}\nالمستخدم: @{c.from_user.username}")
    else:
        bot.answer_callback_query(c.id, "❌ نقاطك لا تكفي!", show_alert=True)

# --- 4. تشغيل كل شيء ---
if __name__ == "__main__":
    start_web_server() # تشغيل السيرفر الوهمي لإرضاء Render
    print("Serever Started...")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
# --- المتجر ---
@bot.message_handler(func=lambda m: m.text == '🛒 متجر الحسابات')
def store(m):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🇺🇸 حساب أمريكي (500 نقطة)", callback_data="buy_us"))
    markup.add(telebot.types.InlineKeyboardButton("🇫🇷 حساب فرنسي (450 نقطة)", callback_data="buy_fr"))
    markup.add(telebot.types.InlineKeyboardButton("🇯🇵 حساب ياباني (600 نقطة)", callback_data="buy_jp"))
    bot.send_message(m.chat.id, "اختر نوع الحساب الذي تريد شراءه بنقاطك:", reply_markup=markup)

# --- معالجة عمليات الشراء ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy(call):
    u = get_user(call.from_user.id)
    prices = {'buy_us': 500, 'buy_fr': 450, 'buy_jp': 600}
    names = {'buy_us': "أمريكي", 'buy_fr': "فرنسي", 'buy_jp': "ياباني"}
    
    price = prices[call.data]
    if u['points'] >= price:
        u['points'] -= price
        bot.answer_callback_query(call.id, "تمت العملية بنجاح!")
        bot.send_message(call.message.chat.id, f"✅ تم شراء حساب {names[call.data]}!\nسيتم إرسال البيانات لك عبر الخاص من قبل الأدمن قريباً.")
        # إشعار للأدمن
        bot.send_message(ADMIN_ID, f"🚨 طلب شراء جديد!\nالمستخدم: @{call.from_user.username}\nالنوع: {names[call.data]}")
    else:
        bot.answer_callback_query(call.id, "❌ نقاطك غير كافية!", show_alert=True)

@bot.message_handler(func=lambda m: m.text == '💰 رصيدي')
def balance(m):
    u = get_user(m.from_user.id)
    bot.reply_to(m, f"💎 رصيدك الحالي: {u['points']} نقطة")

bot.polling(none_stop=True)

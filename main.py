import telebot
import time
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

# --- 1. سيرفر Flask لتجنب إغلاق Render ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online and Ready!"

def run_web(): app.run(host='0.0.0.0', port=8080)

def start_web_server():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. الإعدادات والبيانات ---
API_TOKEN = '8346075393:AAF8vUnRtUj2STFR5aBW47Nnctwn08LXp1A'
ADMIN_ID = 7605020034 
UNIT_ID = '22081' # رقم الـ Block ID فقط
BOT_USERNAME = 'Adsrewards_bot' 

bot = telebot.TeleBot(API_TOKEN)
users_db = {} # {user_id: {'points': 0, 'banned': False, 'name': '', 'last_daily': None, 'referred_by': None}}

def get_u(uid, name=""):
    if uid not in users_db:
        users_db[uid] = {'points': 0, 'banned': False, 'name': name, 'last_daily': None, 'referred_by': None}
    return users_db[uid]

# --- 3. نظام البداية والإحالة ---
@bot.message_handler(commands=['start'])
def welcome(m):
    u = get_u(m.from_user.id, m.from_user.first_name)
    if u['banned']: return bot.send_message(m.chat.id, "🚫 أنت محظور حالياً.")

    # فحص رابط الدعوة
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != m.from_user.id and u['referred_by'] is None:
            u['referred_by'] = ref_id
            get_u(ref_id)['points'] += 15
            bot.send_message(ref_id, f"🎉 سجل صديق جديد عبر رابطك! حصلت على 15 نقطة.")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📺 مشاهدة إعلان (+10)', '🎁 جائزة يومية (+10)')
    markup.add('🛒 متجر الاستبدال', '👥 دعوة الأصدقاء')
    markup.add('💰 رصيدي')
    if m.from_user.id == ADMIN_ID: markup.add('🛠️ لوحة الإدارة')
    
    bot.send_message(m.chat.id, f"🔥 أهلاً بك {m.from_user.first_name} في بوت الأرباح!\nاستبدل نقاطك بأقوى الحسابات العالمية.", reply_markup=markup)

# --- 4. لوحة الإدارة (Admin Panel) ---
@bot.message_handler(func=lambda m: m.text == '🛠️ لوحة الإدارة' and m.from_user.id == ADMIN_ID)
def admin_panel(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📊 إحصائيات', '👤 المستخدمين')
    markup.add('➕ إضافة نقاط', '🚫 حظر مستخدم')
    markup.add('🔙 خروج')
    bot.send_message(m.chat.id, "🛠️ مرحباً أيها المدير، اختر المهمة:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == '📊 إحصائيات')
def stats(m):
    bot.reply_to(m, f"👥 عدد المستخدمين: {len(users_db)}")

# --- 5. المتجر ونظام الاستبدال ---
@bot.message_handler(func=lambda m: m.text == '🛒 متجر الاستبدال')
def shop(m):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("🇺🇸 حساب أمريكي (800 ن)", callback_data="buy_us"))
    kb.add(telebot.types.InlineKeyboardButton("🇫🇷 حساب فرنسي (600 ن)", callback_data="buy_fr"))
    kb.add(telebot.types.InlineKeyboardButton("🇯🇵 حساب ياباني (400 ن)", callback_data="buy_jp"))
    kb.add(telebot.types.InlineKeyboardButton("🎁 جائزة أسبوعية (500 ن)", callback_data="buy_week"))
    bot.send_message(m.chat.id, "🛍️ المتجر: اختر ما تريد استبداله بنقاطك:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('buy_'))
def process_purchase(c):
    prices = {"buy_us": 800, "buy_fr": 600, "buy_jp": 400, "buy_week": 500}
    names = {"buy_us": "حساب أمريكي", "buy_fr": "حساب فرنسي", "buy_jp": "حساب ياباني", "buy_week": "جائزة أسبوعية"}
    
    u = get_u(c.from_user.id)
    price = prices[c.data]
    
    if u['points'] >= price:
        u['points'] -= price
        bot.answer_callback_query(c.id, "✅ تم الطلب بنجاح!")
        bot.send_message(c.message.chat.id, f"✅ تم خصم {price} نقطة مقابل {names[c.data]}. سيتم التواصل معك قريباً.")
        bot.send_message(ADMIN_ID, f"🔔 طلب جديد: {names[c.data]}\n👤 من: [{c.from_user.first_name}](tg://user?id={c.from_user.id})", parse_mode="Markdown")
    else:
        bot.answer_callback_query(c.id, "❌ نقاطك غير كافية!", show_alert=True)

# --- 6. الإعلانات (رابط مباشر) ---
@bot.message_handler(func=lambda m: m.text == '📺 مشاهدة إعلان (+10)')
def show_ad(m):
    u = get_u(m.from_user.id)
    ad_url = f"https://app.adsgram.ai/show?id={UNIT_ID}&userId={m.from_user.id}"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("فتح الإعلان الآن 🔗", url=ad_url))
    
    bot.send_message(m.chat.id, "✅ اضغط على الزر أدناه لمشاهدة الإعلان والحصول على النقاط:", reply_markup=kb)
    u['points'] += 10 # إضافة النقاط (يفضل استخدام ويب هوك للتحقق)

# --- 7. ميزات إضافية (دعوة + يومية + رصيد) ---
@bot.message_handler(func=lambda m: m.text == '👥 دعوة الأصدقاء')
def invite_friends(m):
    link = f"https://t.me/{BOT_USERNAME}?start={m.from_user.id}"
    bot.send_message(m.chat.id, f"🔗 رابطك الخاص للدعوة:\n`{link}`\n\n15 نقطة لكل صديق يسجل!", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '🎁 جائزة يومية (+10)')
def daily_reward(m):
    u = get_u(m.from_user.id)
    now = datetime.now()
    if u['last_daily'] is None or now > u['last_daily'] + timedelta(hours=24):
        u['points'] += 10
        u['last_daily'] = now
        bot.reply_to(m, "✅ استلمت جائزتك اليومية (10 نقاط)!")
    else:
        bot.reply_to(m, "❌ استلمتها بالفعل، عد غداً!")

@bot.message_handler(func=lambda m: m.text == '💰 رصيدي')
def show_balance(m):
    u = get_u(m.from_user.id)
    bot.reply_to(m, f"💎 رصيدك الحالي: {u['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == '🔙 خروج')
def exit_admin(m):
    welcome(m)

if __name__ == "__main__":
    start_web_server()
    print("Bot is Starting...")
    bot.polling(none_stop=True)

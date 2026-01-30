import telebot
import time
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

# --- 1. إعداد السيرفر الوهمي (لبقاء البوت متصلاً على Render) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online! 🚀"

def run_web(): app.run(host='0.0.0.0', port=8080)

def start_web_server():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. الإعدادات الأساسية (تأكد من صحة البيانات) ---
API_TOKEN = '8346075393:AAF8vUnRtUj2STFR5aBW47Nnctwn08LXp1A'
ADMIN_ID = 7605020034 
UNIT_ID = '22081' # رقم الـ Block ID من AdsGram
BOT_USERNAME = 'Adsrewards_bot' # اسم مستخدم البوت بدون @

bot = telebot.TeleBot(API_TOKEN)
users_db = {} # قاعدة بيانات مؤقتة (يُفضل ربطها بـ SQL لاحقاً لحفظ البيانات دائماً)

def get_u(uid, name=""):
    if uid not in users_db:
        users_db[uid] = {'points': 0, 'banned': False, 'name': name, 'last_daily': None, 'referred_by': None}
    return users_db[uid]

# --- 3. نظام التشغيل (Start) والدعوات ---
@bot.message_handler(commands=['start'])
def welcome(m):
    u = get_u(m.from_user.id, m.from_user.first_name)
    if u['banned']: return bot.send_message(m.chat.id, "🚫 عذراً، أنت محظور.")

    # معالجة رابط الإحالة
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != m.from_user.id and u['referred_by'] is None:
            u['referred_by'] = ref_id
            ref_user = get_u(ref_id)
            ref_user['points'] += 15
            bot.send_message(ref_id, f"🎉 انضم صديق جديد عبر رابطك! حصلت على 15 نقطة.")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📺 مشاهدة إعلان (+10)', '🎁 جائزة يومية (+10)')
    markup.add('🛒 متجر الاستبدال', '👥 دعوة الأصدقاء')
    markup.add('💰 رصيدي', '🏆 الجوائز الأسبوعية')
    if m.from_user.id == ADMIN_ID: markup.add('🛠️ لوحة التحكم')
    
    bot.send_message(m.chat.id, f"🔥 أهلاً بك {m.from_user.first_name}!\nاجمع النقاط الآن واستبدلها بأفضل الحسابات.", reply_markup=markup)

# --- 4. حل مشكلة الإعلانات (فتح مباشر) ---
@bot.message_handler(func=lambda m: m.text == '📺 مشاهدة إعلان (+10)')
def ads_service(m):
    u = get_u(m.from_user.id)
    # الرابط المصلح لتجنب صفحة 404 أو الصفحة البيضاء
    ad_url = f"https://app.adsgram.ai/show?id={UNIT_ID}&userId={m.from_user.id}"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("فتح الإعلان الآن 🔗", url=ad_url))
    
    bot.send_message(m.chat.id, "✅ الإعلان جاهز، اضغط أدناه للمشاهدة والحصول على 10 نقاط:", reply_markup=kb)
    u['points'] += 10 # إضافة النقاط عند طلب الإعلان

# --- 5. نظام الجائزة اليومية ودعوة الأصدقاء ---
@bot.message_handler(func=lambda m: m.text == '🎁 جائزة يومية (+10)')
def daily_bonus(m):
    u = get_u(m.from_user.id)
    now = datetime.now()
    if u['last_daily'] is None or now > u['last_daily'] + timedelta(hours=24):
        u['points'] += 10
        u['last_daily'] = now
        bot.reply_to(m, "✅ تم استلام 10 نقاط جائزة يومية! عد غداً.")
    else:
        diff = (u['last_daily'] + timedelta(hours=24)) - now
        hours = diff.seconds // 3600
        bot.reply_to(m, f"❌ لقد استلمت جائزتك بالفعل. عد بعد {hours} ساعة.")

@bot.message_handler(func=lambda m: m.text == '👥 دعوة الأصدقاء')
def invite_link(m):
    link = f"https://t.me/{BOT_USERNAME}?start={m.from_user.id}"
    bot.send_message(m.chat.id, f"🔗 رابط الدعوة الخاص بك:\n`{link}`\n\nستحصل على 15 نقطة لكل شخص يسجل عبرك!", parse_mode="Markdown")

# --- 6. المتجر ونظام الاستبدال ---
@bot.message_handler(func=lambda m: m.text == '🛒 متجر الاستبدال')
def open_shop(m):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("🇺🇸 حساب أمريكي (800 ن)", callback_data="buy_us"))
    kb.add(telebot.types.InlineKeyboardButton("🇫🇷 حساب فرنسي (600 ن)", callback_data="buy_fr"))
    kb.add(telebot.types.InlineKeyboardButton("🇯🇵 حساب ياباني (400 ن)", callback_data="buy_jp"))
    kb.add(telebot.types.InlineKeyboardButton("🎁 جائزة أسبوعية (500 ن)", callback_data="buy_week"))
    bot.send_message(m.chat.id, "🛍️ اختر الحساب الذي تود استبداله:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('buy_'))
def handle_purchase(c):
    prices = {"buy_us": 800, "buy_fr": 600, "buy_jp": 400, "buy_week": 500}
    u = get_u(c.from_user.id)
    price = prices[c.data]
    
    if u['points'] >= price:
        u['points'] -= price
        bot.answer_callback_query(c.id, "✅ تم الطلب!")
        bot.send_message(c.message.chat.id, f"✅ تم خصم {price} نقطة. سيتم إرسال الطلب لك قريباً.")
        bot.send_message(ADMIN_ID, f"🚨 طلب جديد من: [{c.from_user.first_name}](tg://user?id={c.from_user.id})", parse_mode="Markdown")
    else:
        bot.answer_callback_query(c.id, "❌ نقاطك غير كافية!", show_alert=True)

# --- 7. لوحة التحكم والإحصائيات ---
@bot.message_handler(func=lambda m: m.text == '💰 رصيدي')
def check_balance(m):
    u = get_u(m.from_user.id)
    bot.reply_to(m, f"💎 رصيدك الحالي: {u['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == '🛠️ لوحة التحكم' and m.from_user.id == ADMIN_ID)
def admin_panel(m):
    bot.send_message(m.chat.id, f"📊 إحصائيات البوت:\n👥 عدد المستخدمين: {len(users_db)}")

# --- تشغيل البوت ---
if __name__ == "__main__":
    start_web_server()
    print("Bot is Starting...")
    bot.polling(none_stop=True)

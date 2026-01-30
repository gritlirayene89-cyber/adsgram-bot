import telebot
import time

# بياناتك الخاصة
API_TOKEN = '8346075393:AAF8vUnRtUj2STFR5aBW47Nnctwn08LXp1A'
ADMIN_ID = 7605020034 # لاستقبال طلبات الحسابات
UNIT_ID = 'bot-22081' 

bot = telebot.TeleBot(API_TOKEN)

# قاعدة بيانات مؤقتة (للتجربة)
users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {'points': 0}
    return users[uid]

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📺 مشاهدة إعلان (+10 نقاط)')
    markup.add('🛒 متجر الحسابات', '💰 رصيدي')
    markup.add('🎁 الجوائز الأسبوعية')
    bot.send_message(m.chat.id, "🔥 أهلاً بك! اجمع النقاط واستبدلها بحسابات عالمية.", reply_markup=markup)

# --- نظام الإعلانات ---
@bot.message_handler(func=lambda m: m.text == '📺 مشاهدة إعلان (+10 نقاط)')
def show_ad(m):
    u = get_user(m.from_user.id)
    ad_url = f"https://adsgram.ai/show?id={UNIT_ID}&userId={m.from_user.id}"
    
    # هنا نفترض أن المستخدم شاهد الإعلان (في النسخة الاحترافية نحتاج Webhook للتأكد)
    u['points'] += 10
    bot.send_message(m.chat.id, f"✅ تم إضافة 10 نقاط لرصيدك!\nرابط الإعلان للدعم:\n{ad_url}")

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

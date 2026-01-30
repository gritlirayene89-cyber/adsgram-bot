import telebot
import time

# بياناتك الخاصة
API_TOKEN = '8346075393:AAF8vUnRtUj2STFR5aBW47Nnctwn08LXp1A'
ADMIN_ID = 7605020034
UNIT_ID = 'bot-22081' 
bot = telebot.TeleBot(API_TOKEN)

users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {'points': 0, 'last_ad': 0}
    return users[uid]

@bot.message_handler(commands=['start'])
def start(m):
    user = get_user(m.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📺 مشاهدة إعلان (+10)', '👥 دعوة صديق (+10)')
    markup.add('🛒 المتجر', '💰 رصيدي', '🎁 طلب سحب')
    bot.send_message(m.chat.id, "🔥 أهلاً بك! اجمع النقاط واستبدلها بحسابات جاهزة.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '📺 مشاهدة إعلان (+10)')
def ads(m):
    u = get_user(m.from_user.id)
    now = time.time()
    if now - u['last_ad'] < 600:
        bot.reply_to(m, f"⚠️ انتظر {int(600-(now-u['last_ad']))//60} دقيقة.")
    else:
        # نظام مكافأة يدوي مبسط
        u['points'] += 10
        u['last_ad'] = now
        ad_url = f"https://adsgram.ai/show?id={UNIT_ID}&userId={m.from_user.id}"
        bot.send_message(m.chat.id, f"تفضل الإعلان، شاهده كاملاً لضمان نقاطك:\n{ad_url}")

@bot.message_handler(func=lambda m: m.text == '💰 رصيدي')
def bal(m):
    bot.reply_to(m, f"💎 رصيدك الحالي: {get_user(m.from_user.id)['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == '🛒 المتجر')
def shop(m):
    bot.send_message(m.chat.id, "🇺🇸 أمريكي: 320ن\n🇫🇷 فرنسي: 300ن\n🇯🇵 ياباني: 280ن\n🏆 مسابقة أسبوعية: 250ن")

@bot.message_handler(func=lambda m: m.text == '🎁 طلب سحب')
def req(m):
    u = get_user(m.from_user.id)
    if u['points'] >= 250:
        bot.send_message(ADMIN_ID, f"🚨 طلب سحب!\nالمستخدم: @{m.from_user.username}\nID: {m.from_user.id}\nالنقاط: {u['points']}")
        bot.reply_to(m, "✅ تم إرسال طلبك بنجاح.")
    else:
        bot.reply_to(m, "❌ رصيدك أقل من 250 نقطة.")

bot.polling(none_stop=True)

import telebot
import yt_dlp
import os

# --- الإعدادات الآمنة ---
# سيقوم البوت بقراءة التوكن من إعدادات السيرفر مباشرة
API_TOKEN = os.getenv('BOT_TOKEN') 

if not API_TOKEN:
    print("❌ خطأ: لم يتم العثور على BOT_TOKEN في إعدادات النظام!")
    exit()

bot = telebot.TeleBot(API_TOKEN)

# إعدادات التحميل
YDL_OPTIONS = {
    'format': 'best',
    'outtmpl': 'video_%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
    },
    'quiet': False,
    'no_warnings': True,
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 أهلاً بك! أرسل لي رابط فيديو من (يوتيوب، فيسبوك، تيك توك، إنستغرام) وسأقوم بتحميله.")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_download(message):
    url = message.text
    status_msg = bot.reply_to(message, "⏳ جاري محاولة سحب الفيديو... انتظر قليلاً")
    
    filename = None # تعريف مسبق لتجنب أخطاء حذف الملف
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            video_title = info.get('title', 'فيديو بدون عنوان')

        with open(filename, 'rb') as video_file:
            bot.send_video(
                message.chat.id, 
                video_file, 
                caption=f"✅ تم التحميل: {video_title}",
                reply_to_message_id=message.message_id
            )
        
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        error_text = str(e)
        bot.edit_message_text(f"❌ حدث خطأ: {error_text[:100]}...", message.chat.id, status_msg.message_id)
    
    finally:
        # التأكد من حذف الملف دائماً لتوفير مساحة السيرفر
        if filename and os.path.exists(filename):
            os.remove(filename)

print("✅ البوت يعمل الآن...")
bot.infinity_polling()


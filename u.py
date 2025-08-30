from telegram.ext import Updater, CommandHandler
import json
import os

# Your Bot Token
BOT_TOKEN = "7876769050:AAFMXC8PSrwNszlq4nkcMAtr069plyn_76A"

# JSON file to store scammer database
DB_FILE = "scammer_db.json"

# ⚠️ Your Telegram User ID (Admin)
ADMIN_ID = 7586013235  

# Load or create scammer database
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        scammer_db = json.load(f)
else:
    scammer_db = {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(scammer_db, f, indent=2)

def start(update, context):
    update.message.reply_text(
        "👋 Welcome!\n\n"
        "Commands:\n"
        "🔍 /check <number> → Check if number is a scam\n"
        "⚠️ /report <number> <reason> → Report a scammer number\n"
        "📋 /list → Show all reported scam numbers\n"
        "📊 /stats → Show scam database statistics\n"
        "🔎 /search <keyword> → Search scam reports by keyword\n"
        "🛠️ (Admin only) /remove <number> → Delete a number from database"
    )

def check_number(update, context):
    if len(context.args) == 0:
        update.message.reply_text("❌ Please provide a number.\nExample: `/check 9876543210`", parse_mode="Markdown")
        return
    
    number = context.args[0]
    if number in scammer_db:
        reports = "\n".join([f"- {r}" for r in scammer_db[number]])
        reply = f"🔎 Result for {number}:\n\n⚠️ Reported as Scam\n📋 Reports:\n{reports}"
    else:
        reply = f"✅ {number} is *not reported* in the database.\n\n(You can /report it if it’s a scam.)"
    
    update.message.reply_text(reply, parse_mode="Markdown")

def report_number(update, context):
    if len(context.args) < 2:
        update.message.reply_text("❌ Usage: /report <number> <reason>")
        return
    
    number = context.args[0]
    reason = " ".join(context.args[1:])
    
    if number not in scammer_db:
        scammer_db[number] = []
    
    scammer_db[number].append(reason)
    save_db()
    
    update.message.reply_text(
        f"✅ Thanks! Number {number} has been reported.\nReason: {reason}"
    )

def list_numbers(update, context):
    if not scammer_db:
        update.message.reply_text("✅ No scam numbers reported yet.")
        return
    
    message = "📋 Reported Scam Numbers:\n\n"
    for number, reasons in scammer_db.items():
        message += f"📞 {number}\n"
        for r in reasons:
            message += f"   - {r}\n"
        message += "\n"
    
    for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
        update.message.reply_text(chunk)

def remove_number(update, context):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    
    if len(context.args) == 0:
        update.message.reply_text("❌ Usage: /remove <number>")
        return
    
    number = context.args[0]
    if number in scammer_db:
        del scammer_db[number]
        save_db()
        update.message.reply_text(f"🗑️ Number {number} has been removed from the database.")
    else:
        update.message.reply_text(f"❌ Number {number} not found in database.")

def stats(update, context):
    total_numbers = len(scammer_db)
    total_reports = sum(len(reasons) for reasons in scammer_db.values())
    update.message.reply_text(
        f"📊 Scam Database Stats:\n\n"
        f"📞 Total scam numbers: {total_numbers}\n"
        f"📝 Total reports: {total_reports}"
    )

def search_reports(update, context):
    if len(context.args) == 0:
        update.message.reply_text("❌ Usage: /search <keyword>\nExample: `/search OLX`", parse_mode="Markdown")
        return
    
    keyword = " ".join(context.args).lower()
    results = []
    
    for number, reasons in scammer_db.items():
        for r in reasons:
            if keyword in r.lower():
                results.append(f"📞 {number} → {r}")
    
    if not results:
        update.message.reply_text(f"❌ No scam reports found with keyword: {keyword}")
        return
    
    message = f"🔎 Search Results for *{keyword}*:\n\n" + "\n".join(results)
    
    for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
        update.message.reply_text(chunk, parse_mode="Markdown")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check", check_number))
    dp.add_handler(CommandHandler("report", report_number))
    dp.add_handler(CommandHandler("list", list_numbers))
    dp.add_handler(CommandHandler("remove", remove_number))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("search", search_reports))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

tap_counts = {}
leaderboard = {}

GAME_DURATION = 30  # seconds

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tap_counts[user_id] = 0

    keyboard = [[InlineKeyboardButton("Tap! 🧉", callback_data="tap")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎉 Hey {update.effective_user.first_name}! Game started!\n"
        f"Tap the button as many times as you can in {GAME_DURATION} seconds!",
        reply_markup=reply_markup
    )

    await asyncio.sleep(GAME_DURATION)

    score = tap_counts.get(user_id, 0)
    leaderboard[user_id] = score
    tap_counts.pop(user_id, None)

    await update.message.reply_text(
        f"⏰ Time's up! You tapped {score} times. Nice job! 🥳\n"
        f"Use /leaderboard to see the top players."
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in tap_counts:
        tap_counts[user_id] += 1
        await query.answer(text=f"Taps: {tap_counts[user_id]}")
    else:
        await query.answer(text="Start a game first by sending /startgame")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not leaderboard:
        await update.message.reply_text("No scores yet. Play a game with /startgame!")
        return

    sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]

    text = "🏆 LassiInu Tap Game Leaderboard 🏆\n"
    for i, (user_id, score) in enumerate(sorted_board, 1):
        user = await context.bot.get_chat(user_id)
        username = user.first_name if user else f"User {user_id}"
        text += f"{i}. {username}: {score} taps\n"

    await update.message.reply_text(text)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not set.")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("startgame", startgame))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_lang'] = 'ko'  # Default to Korean
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ask Question", callback_data="ask_question")],
        [InlineKeyboardButton("Change Language", callback_data="change_lang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What would you like to do?", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ask_question":
        await query.edit_message_text("Please type your question or statement.")
        context.user_data['awaiting_input'] = True
    elif query.data == "change_lang":
        keyboard = [
            [InlineKeyboardButton("Korean", callback_data="lang_ko")],
            [InlineKeyboardButton("English", callback_data="lang_en")],
            [InlineKeyboardButton("Japanese", callback_data="lang_ja")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a language:", reply_markup=reply_markup)
    elif query.data.startswith("lang_"):
        lang = query.data.split("_")[1]
        context.user_data['current_lang'] = lang
        await query.edit_message_text(f"Language changed to {lang}")
        await show_main_menu(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_input'):
        user_input = update.message.text
        lang = context.user_data.get('current_lang', 'ko')
        
        response = await generate_response(user_input, lang)
        
        await update.message.reply_text(response)
        context.user_data['awaiting_input'] = False
        await show_main_menu(update, context)
    else:
        await update.message.reply_text("I'm not sure how to respond to that. Please use the menu options.")

async def generate_response(user_input, lang):
    language_prompts = {
        'ko': "다음 질문이나 언급에 대해 한국어로 답변해주세요:",
        'en': "Please respond to the following question or statement in English:",
        'ja': "以下の質問または発言に日本語で答えてください："
    }

    prompt = f"{language_prompts[lang]} {user_input}"

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in the specified language."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        return "Sorry, I couldn't generate a response at this time."

async def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Bot is running...")
    
    try:
        await asyncio.Event().wait()
    finally:
        logger.info("Bot is shutting down...")
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Error occurred: {e}")
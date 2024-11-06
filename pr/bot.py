from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *


# тут будем писать наш код :)


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    else:
        await send_text(update, context, "Привет!")
        await send_text(update, context, "Как дела, *дружище*?")
        await send_text(update, context, "Ты написал " + update.message.text)


async def hello_button(update, context):
    query = update.callback_query.data  #код кнопки
    await update.callback_query.answer()  #помечаем что обработали нажатие на кнопку
    await send_html(update, context, "Вы нажали на кнопку " + query)


async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await show_main_menu(update, context, {
    "start": "главное меню бота",
    "profile": "ггенерация Tinder-профля 😎",
    "opener": "сообщение для знакомства 🥰 ",
    "message": "переписка от вашего имени 😈",
    "date": "переписка со звездами 🔥",
    "gpt": "задать вопрос чату GPT 🧠"
})

async def gpt(update, context):
    dialog.mode = "gpt"
    await send_photo(update, context, "gpt")
    await send_text(update, context, "Напишите сообщение *ChatGPT*:")


async def date(update, context):
    dialog.mode = 'date'
    text = 'Hello it is date!'
    await send_text_buttons(update, context, text, {
        "date_gosling": " Райан Гослинг",
        "date_robbie": "Робби Марго",
        "date_hardy": "Тои Харди"
    })


async def gpt_dialog(update, context):
    my_message = await send_text(update, context, "ChatGPT думает. Ожидайте...")
    prompt = load_prompt("gpt")
    text = update.message.text
    print(update.message.text)
    answer = await chatgpt.send_question(prompt, text)
    await my_message.edit_text(answer)
    await send_text(update, context, answer)


async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Девушка набирает текст...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(update, context, " Отличный выбор! ")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


dialog = Dialog()
dialog.mode = 'main'
dialog.list = []

async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def message(update, context):
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next": "Написать сообщение",
        "message_date": "Пригласить на свидание",
    })
    dialog.list.clear()


async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update, context, "ChatGPT думает над вариантами ответа...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


chatgpt = ChatGptService(
    token="gpt:--mRNrTISss9Vj3Q6lCoImv5cXw51H8RE70DG7rsRaf4bEE4")

app = ApplicationBuilder().token("7346802944:AAE-").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))


app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))

#
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # отключаем команды

app.add_handler(CallbackQueryHandler(hello_button))

dialog = Dialog()
dialog.mode = "main"
app.run_polling()

from telegram import Bot
import asyncio


BOT_TOKEN = "7486031611:AAFnGSrsiU_2mtoeCTOJYpQh5mVTj5csuC4"
bot = Bot(token=BOT_TOKEN)


async def send_notification(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Message sent to {chat_id}: {message}")
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")


def notify_new_borrowing(borrowing_details):
    message = f"Створено нове позичання:\n{borrowing_details}"
    chat_id = "843682530"
    asyncio.run(send_notification(chat_id, message))


def notify_overdue_borrowing(borrowing_details):
    message = f"Прострочене позичання:\n{borrowing_details}"
    chat_id = "843682530"
    asyncio.run(send_notification(chat_id, message))


def notify_successful_payment(payment_details):
    message = f"Оплата успішна:\n{payment_details}"
    chat_id = "843682530"
    asyncio.run(send_notification(chat_id, message))

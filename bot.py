from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import logging

from database import create_connection, find_client_by_contract_number # database, поиск клиента в БД

# включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


TOKEN = '7929072595:AAGO11uzddCpSGgqER4MMfUpPsc2CcGSn_Q'

user_data = {}
auser_data = {}

conn = create_connection("clients.db") # connection 


###проверка на валидность !!!
def is_valid_phone_number(number: str) -> bool:
    """Проверяет, является ли номер телефона валидным."""
    
    # удаляем пробелы
    number = number.replace(" ", "")
    
    # удаляем все нецифровые символы
    filtered_number = ''.join(char for char in number if char.isdigit())
    
    # проверяем на формат номера
    if filtered_number.startswith("7"):
        filtered_number = "8" + filtered_number[1:]
    
    if len(filtered_number) == 11:
        return True
    else:
        return False

# дерево сценариев 
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [['Войти как клиент ТТК', 'Заключить новый договор']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text('Добро пожаловать! Выберите опцию:', reply_markup=reply_markup)

# сценарий 1
async def handle_client_login(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    user_data[user_id] = {'stage': 'check_contract_number'}  # Устанавливаем стадию
    await update.message.reply_text('Вы выбрали "Войти как клиент ТТК". Пожалуйста, введите номер договора (пример: 516xxxxxx):')

#


# сценарий 2
async def handle_new_contract(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    user_data[user_id] = {'stage': 'contact_number'}  # устанавливаем стадию
    await update.message.reply_text('Вы выбрали "Заключить новый договор". Укажите ваш контактный номер.')


async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    stage = user_data.get(user_id, {}).get('stage')

# сценарий 1
    if stage == 'contact_number':
        contact_number = update.message.text

        # проверяем валидность номера
        if is_valid_phone_number(contact_number):
            user_data[user_id]['contact_number'] = contact_number  # сохраняем номер
            user_data[user_id]['stage'] = 'installation_address'  # переходим к следующему этапу
            await update.message.reply_text('Спасибо! Теперь укажите место, где провести установку услуги (например, адрес).')
        else:
            await update.message.reply_text('Неверный формат номера. Пожалуйста, укажите номер в формате "+7XXXXXXXXXX" или "8XXXXXXXXXX".')

    elif stage == 'installation_address':
        installation_address = update.message.text
        user_data[user_id]['installation_address'] = installation_address  # сохраняем адрес
        user_data[user_id]['stage'] = None  # сбрасываем стадию
        await update.message.reply_text(f'Ваш контактный номер "{user_data[user_id]["contact_number"]}" и адрес установки "{installation_address}" сохранены. Спасибо!')
    
    # сценарий "ттк клиент" 
    elif stage == 'check_contract_number':
        contract_number = update.message.text

        # проверка на валидность
        if len(contract_number) == 9 and contract_number.startswith('516') and contract_number[3:].isdigit():
            client_name = find_client_by_contract_number(conn, contract_number)
            if client_name:
                await update.message.reply_text(f'Здравствуйте, {client_name}! Что бы вы хотели сделать?')

                # ИСПРАВИТЬ добавить стейдж ЗАПРОСА  
                user_data[user_id]['stage'] = None
                
            else:
                await update.message.reply_text('Клиент с таким номером договора не найден. Попробуйте еще раз.')
        else:
            await update.message.reply_text('Неверный формат номера договора. Пожалуйста, введите номер как "516xxxxxx".')

    
    else:
        await update.message.reply_text('Пожалуйста, выберите опцию или введите команду /start.')

    

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Regex('^Войти как клиент ТТК$'), handle_client_login))
    app.add_handler(MessageHandler(filters.Regex('^Заключить новый договор$'), handle_new_contract))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
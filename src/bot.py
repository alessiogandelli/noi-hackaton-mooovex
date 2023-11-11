from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackContext
from telegram.ext import filters, MessageHandler, Updater
import os 
from dotenv import load_dotenv
import subprocess
from text_processor import speech_to_text, parse_trip, get_place_id, search_route, confirm_trip
WAITING_FOR_REPLY = 1
load_dotenv()

convert_script = "src/ogg_to_mp3.sh"
input_file = "data/taxi.ogg"

TOKEN = os.getenv("BOT_TOKEN")

async def save_file(context, update):
    file = await context.bot.get_file(update.message.voice.file_id)

    print("file_id: " + str(update.message.voice.file_id))
    #save file 
    with open('data/taxi.ogg', 'wb') as f:
        await file.download_to_memory(f)
    
    #convert file
    subprocess.call([convert_script, input_file])


async def handle_audio(update: Update, context: CallbackContext) -> None:

    await save_file(context, update)
    transcript = speech_to_text()
    print(transcript)
    trip = parse_trip(transcript)
    context.user_data['trip'] = trip

    await update.message.reply_text(trip)

    #place_id_start, place_id_end = get_place_id(trip, context, update)
    #print(place_id_start, place_id_end)

    return WAITING_FOR_REPLY
    #await process_audio(update, context)

async def process_audio(update: Update, context: CallbackContext):
    transcript = speech_to_text()
    print(transcript)
    trip = parse_trip(transcript)

    await update.message.reply_text(trip)

    #place_id_start, place_id_end = get_place_id(trip, context, update)
    #print(place_id_start, place_id_end)

    return WAITING_FOR_REPLY
    
    #route = search_route(place_id_start, place_id_end, trip)

    #update.message.reply_text(f'Your trip start at {route.origin_place.formatted_address} \n and end at {route.destination_place.formatted_address} \n the price is {route.price}')


async def handle_reply(update: Update, context: CallbackContext) -> None:

    await save_file(context, update)
    
    transcript = speech_to_text()
    answer = confirm_trip(transcript)
    #to lowercase
    answer = answer.lower()
    #remove punctuation
    answer = answer.replace(".", "")

    if answer == "yes" or answer == "ja" or answer == "si":
        await update.message.reply_text("confirmed")
        trip = context.user_data['trip']
        place_id_start, place_id_end = get_place_id(trip, context, update)
        route = search_route(place_id_start, place_id_end, trip)

        msg = 'start: '+route['origin_place']['formatted_address'] + '\n'
        msg += 'end: '+route['destination_place']['formatted_address'] + '\n'
        msg += 'price: '+str(route['price']) + '\n'
        await update.message.reply_text(msg)

    else:
        await update.message.reply_text("not confirmed")

    return ConversationHandler.END

def main() -> None:
    
    app = ApplicationBuilder().token(TOKEN).build()


    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.VOICE, handle_audio)],
        states={
                WAITING_FOR_REPLY: [MessageHandler(filters.VOICE & ~filters.COMMAND, handle_reply)],
            },
        fallbacks=[CommandHandler('cancel', lambda update, context: ConversationHandler.END)],
    )
    #app.add_handler(MessageHandler(filters.VOICE, handle_audio))
    app.add_handler(conv_handler)



    app.run_polling()


if __name__ == '__main__':
    main()
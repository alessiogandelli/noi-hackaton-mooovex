from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackContext
from telegram.ext import filters, MessageHandler, Updater
import os 
from dotenv import load_dotenv
import subprocess
from text_processor import speech_to_text, parse_trip, get_place_id, search_route

load_dotenv()

convert_script = "src/ogg_to_mp3.sh"
input_file = "data/taxi.ogg"

TOKEN = os.getenv("BOT_TOKEN")



async def handle_audio(update: Update, context: CallbackContext) -> None:
    file = await context.bot.get_file(update.message.voice.file_id)

    print("file_id: " + str(update.message.voice.file_id))
    #save file 
    with open('data/taxi.ogg', 'wb') as f:
        await file.download_to_memory(f)
    
    #convert file
    subprocess.call([convert_script, input_file])
    process_audio()

def process_audio():
    transcript = speech_to_text()
    print(transcript)
    trip = parse_trip(transcript)
    print(trip)
    place_id_start, place_id_end = get_place_id(trip)
    print(place_id_start, place_id_end)
    route = search_route(place_id_start, place_id_end, trip)

    print(route)

def main() -> None:
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.VOICE, handle_audio))

    # clean data folder 
    subprocess.call(["rm", "data/taxi.ogg"])
    subprocess.call(["rm", "data/taxi.mp3"])

    app.run_polling()


if __name__ == '__main__':
    main()
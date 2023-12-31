from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackContext
from telegram.ext import filters, MessageHandler, Updater
import os 
from dotenv import load_dotenv
from text_processor import *

WAITING_FOR_REPLY = 1
WAITING_FOR_PASSANGERS = 2
load_dotenv()

convert_script = "src/ogg_to_mp3.sh"
input_file = "data/taxi.ogg"

TOKEN = os.getenv("BOT_TOKEN")


#------------------Message Handlers------------------#

# first step, receive trip info from the driver, (start, destination, number of passangers, date, time)
async def handle_audio(update: Update, context: CallbackContext) -> None:

    print('--handle audio')

    await listen_audio(context, update)
    transcript = speech_to_text() # transcript the audio
    print(transcript)   
    # parse the text to extract the fields
    trip = parse_trip(transcript) 
    context.user_data['trip'] = trip

    # se il numero di passeggeri è null, chiedi quanti sono
    if trip['number_of_passengers'] == None:
        if trip['language'] == 'it':
            text_to_speech("quanti passeggeri?")
        elif trip['language'] == 'en':
            text_to_speech("how many passengers?")
        elif trip['language'] == 'de':
            text_to_speech("wie viele passagiere?")
        await update.message.reply_voice(voice=open('data/reply.mp3', 'rb'))
        trip = context.user_data['trip']
        return WAITING_FOR_PASSANGERS
    
    else:
        trip = context.user_data['trip']
        place_id_start, place_id_end = get_place_id(trip, context, update)
        if place_id_start == None:
            await update.message.reply_text("start not found")
            return ConversationHandler.END
    
        if place_id_end == None:
            await update.message.reply_text("end not found")
            return ConversationHandler.END
        
        route = search_route(place_id_start, place_id_end, trip)

        #print(route)


        reply = generate_reply(route, trip)

        text_to_speech(reply)

        await update.message.reply_voice(voice=open('data/reply.mp3', 'rb'))

        return WAITING_FOR_REPLY

# receive the number of passangers and then queries the trip to the api 
async def handle_passangers(update: Update, context: CallbackContext) -> None:
    print('--handle passangers')
    await listen_audio(context, update)
    transcript = speech_to_text()
    answer = number_of_passangers(transcript)

    context.user_data['trip']['number_of_passengers'] = answer



    if answer < 8:
        await update.message.reply_text('number of passengers: '+str(answer))
        trip = context.user_data['trip']
        place_id_start, place_id_end = get_place_id(trip, context, update)
        if place_id_start == None:
            await update.message.reply_text("start not found try again")
            return ConversationHandler.END
    
        if place_id_end == None:
            await update.message.reply_text("end not found try again")
            return ConversationHandler.END
        
        route = search_route(place_id_start, place_id_end, trip)
        #print(route)
 

        reply = generate_reply(route, trip)

        text_to_speech(reply)

        await update.message.reply_voice(voice=open('data/reply.mp3', 'rb'))




        return WAITING_FOR_REPLY
    else:
        if trip['language'] == 'en':
            text_to_speech("number of passangers not valid, try again")
        elif trip['language'] == 'it':
            text_to_speech("numero di passeggeri non valido, riprova")
        elif trip['language'] == 'de':
            text_to_speech("anzahl der passagiere nicht gültig, versuchen sie es erneut")

        await update.message.reply_voice(voice=open('data/reply.mp3', 'rb'))

# waits for confirmation and then depending on the affirmative or negative answer, confirms the trip or not
async def handle_reply(update: Update, context: CallbackContext) -> None:
    print('--handle confirm')
    await listen_audio(context, update) # listen audio 
    
    transcript = speech_to_text() # transcript audio
    answer = confirm_trip(transcript) # get yes or not 
    answer = answer.lower().replace(".", "")#to lowercase and remove punctiation


    #confirm the trip 
    if answer == "yes" or answer == "ja" or answer == "si":
        await update.message.reply_text("confirmed")
    # do not confirm the trip 
    else:
        await update.message.reply_text("not confirmed, riprova")

    return ConversationHandler.END
    
def main() -> None:
    
    # create bot 
    app = ApplicationBuilder().token(TOKEN).build()

    # conversation handler, starts with handle_audio, then goes to handle_reply, if no passangers are provided goes to handle_passangers and then to handle_reply
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.VOICE, handle_audio)],
        states={
                WAITING_FOR_REPLY: [MessageHandler(filters.VOICE & ~filters.COMMAND, handle_reply)],
                WAITING_FOR_PASSANGERS: [MessageHandler(filters.VOICE & ~filters.COMMAND, handle_passangers)]
                
            },
        fallbacks=[CommandHandler('cancel', lambda update, context: ConversationHandler.END)],
    )
    #app.add_handler(MessageHandler(filters.VOICE, handle_audio))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == '__main__':
    main()
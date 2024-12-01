from flask import Flask, render_template, redirect, url_for
import threading
import logging
import time
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import MemorySession

# Initialize Flask app
app = Flask(__name__)

# API credentials for Telegram (replace with your actual credentials)
api_id = 23679868
api_hash = 'eebd9bca724210a098f3f4b23822d1ef'

# Use in-memory session to avoid using a file-based session
client = TelegramClient(MemorySession(), api_id, api_hash)

# Start/stop flags
is_running = False

# This message can contain any text, links, and emoji
message = "\n'"

# Set up logging
logging.basicConfig(level=logging.INFO)

# This function is responsible for handling new messages in Telegram
@client.on(events.NewMessage())
async def handler(event):
    try:
        logging.info(f"Received message from {event.sender_id}: {event.message.text}")

        # Logic for filtering messages and responding
        if not event.is_private:
            sender = await event.get_sender()
            sender_username = sender.username if sender.username else ""
            sender_user_id = sender.id

            # List of usernames to exclude
            exclude_usernames = [
                'vaishu9630','Universe9911','salbahepadin01','B4DCHILDD','xinchenganna','online7259','alwayssalbahe_kram',
                'depressedpasayo','xinchengxiaoli','salbahenga','ILABYOUACEZYYY','Xincheng_Nikkkkkk','Saaalbahemeh',
                'zariiiii_aaahh','LOUIE67889','DDAANNAAYYA','Xincheng_dayy','Angelaaaa0000000','BurgerkaaasakenBrrt',
                'anna123abc1','DAANNAAYYAA','zhangmei123','xiaolong1123452','xiaohao66883','ILABYOUNGA','ameizxc',
                'xincheng_nik','Xincheng_fei','countNumber1Bot','supermegabigb0y','superbigboOoy','Goldy6522','BurgerkaaasakenBrrt'
            ]

            # List of user IDs to exclude
            exclude_user_ids = [7716075514]  # Add more user IDs as needed

            # Exclude messages from filtered users and specific texts
            if sender_username not in exclude_usernames and sender_user_id not in exclude_user_ids:
                exclude_texts = ['单笔费用', 'cancel', 'update', 'UPDATE', 'CANCEL']
                exclude_characters = ["'", '.', ';', '0']

                if not any(text in event.message.text for text in exclude_texts):
                    text_without_excluded_characters = ''.join([char for char in event.message.text if char not in exclude_characters])
                    if text_without_excluded_characters.strip():
                        await event.reply(message)
                        logging.info("Replied to the message")
                    else:
                        logging.info("Message contains only excluded characters")
                else:
                    logging.info("Excluded message due to specific text")
            else:
                logging.info("Message did not meet criteria for a reply or is from an excluded username or user ID")
        else:
            logging.info("Message is from a private chat, excluding from reply")
    except Exception as e:
        logging.error(f"Error handling message: {e}")

# Main function to start the bot
async def main():
    await client.start()  # This will ask for phone number and OTP if not already logged in
    logging.info("Client started")
    await client.run_until_disconnected()

# Start the bot in a separate thread
def start_telegram_bot():
    loop = asyncio.new_event_loop()  # Create a new event loop for the thread
    asyncio.set_event_loop(loop)  # Set the new event loop as the current loop for the thread
    try:
        loop.run_until_complete(main())  # Start the event loop
    except Exception as e:
        logging.error(f"Error: {e}")
        time.sleep(5)  # Reconnect in 5 seconds on error

# Routes for Flask app
@app.route('/')
def index():
    return render_template('index.html', is_running=is_running)

@app.route('/start')
def start():
    global is_running
    if not is_running:
        is_running = True
        threading.Thread(target=start_telegram_bot).start()  # Start bot in a new thread
    return redirect(url_for('index'))

@app.route('/stop')
def stop():
    global is_running
    if is_running:
        is_running = False
        client.disconnect()  # Gracefully disconnect the bot
    return redirect(url_for('index'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Run the Flask app on port 5000

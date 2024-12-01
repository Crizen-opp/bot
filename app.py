from flask import Flask, render_template, request, redirect, url_for, session
import threading
import logging
import time
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import MemorySession

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

# API credentials for Telegram (replace with your actual credentials)
api_id = 23679868
api_hash = 'eebd9bca724210a098f3f4b23822d1ef'

# Global variables
client = None
is_running = False
phone_number = None

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to authenticate the Telegram client
async def authenticate(phone_number):
    global client
    client = TelegramClient(MemorySession(), api_id, api_hash)
    await client.start(phone_number)
    logging.info("Client started")

    # Handle OTP if required
    if not await client.is_user_authorized():
        logging.info("OTP required, please check your Telegram for the code.")
        return False  # OTP will be sent to the phone number
    logging.info("Client authenticated")
    return True

# Function to handle new messages
async def handle_new_message(event):
    try:
        logging.info(f"Received message from {event.sender_id}: {event.message.text}")
        message = "\n'"  # Define message to send

        # Logic for filtering messages and responding
        if not event.is_private:
            sender = await event.get_sender()
            sender_username = sender.username if sender.username else ""
            sender_user_id = sender.id

            exclude_usernames = ['vaishu9630', 'Universe9911', 'salbahepadin01']  # List of usernames to exclude
            exclude_user_ids = [7716075514]  # List of user IDs to exclude

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

# Function to start the bot
async def start_bot():
    global client
    # Attach the event handler once client is started
    client.add_event_handler(handle_new_message, events.NewMessage())
    await client.run_until_disconnected()

# Start the bot in a separate thread
def start_telegram_bot():
    try:
        asyncio.run(start_bot())  # Run the bot using the default event loop
    except Exception as e:
        logging.error(f"Error: {e}")
        time.sleep(5)  # Reconnect in 5 seconds on error

@app.route('/')
def index():
    return render_template('index.html', is_running=is_running)

@app.route('/authenticate', methods=['POST'])
def authenticate_route():
    global phone_number, is_running
    phone_number = request.form['phone_number']

    # Start the authentication process
    success = asyncio.run(authenticate(phone_number))
    if success:
        is_running = True
        # Start the bot now that the client is authenticated
        threading.Thread(target=start_telegram_bot, daemon=True).start()
    else:
        return render_template('otp_form.html', phone_number=phone_number)  # OTP input form
    return redirect(url_for('authenticate'))

@app.route('/authenticate_otp', methods=['POST'])
def authenticate_otp():
    global client, is_running
    otp = request.form['otp']
    
    # Sign in with OTP
    if client:
        asyncio.run(client.sign_in(phone_number, otp))
        is_running = True  # Authentication successful
        threading.Thread(target=start_telegram_bot, daemon=True).start()
    return redirect(url_for('authenticate'))

@app.route('/stop')
def stop():
    global is_running
    if is_running:
        is_running = False
        if client:
            client.disconnect()  # Gracefully disconnect the bot
    return redirect(url_for('authenticate'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Run the Flask app on port 5000

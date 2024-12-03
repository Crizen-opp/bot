import os
import base64
from flask import Flask, render_template, request, redirect, url_for
import threading
import logging
import asyncio
from telethon import TelegramClient, events, errors
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

# Function to load the session from environment variable and save it as user.session file
def load_session_from_env():
    encoded_session = os.environ.get('USER_SESSION')
    if encoded_session:
        try:
            # Decode the base64 string
            decoded_session = base64.b64decode(encoded_session)

            # Save it as a user.session file
            with open('user.session', 'wb') as f:
                f.write(decoded_session)
            logging.info("Session loaded from environment variable.")
        except Exception as e:
            logging.error(f"Failed to decode and save session: {e}")
    else:
        logging.error("No USER_SESSION environment variable found.")

# Call the function to load the session at the start of the app
load_session_from_env()

# Function to authenticate the Telegram client
async def authenticate(phone_number):
    global client
    client = TelegramClient('user.session', api_id, api_hash)
    
    try:
        await client.connect()
        await client.send_code_request(phone_number)
        return True  # OTP is required
    except errors.rpcerrorlist.PhoneNumberInvalidError:
        logging.error("Invalid phone number")
        return False
    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        return False

# Function to handle new messages
async def handle_new_message(event):
    try:
        logging.info(f"Received message from {event.sender_id}: {event.message.text}")
        if not event.is_private:
            sender = await event.get_sender()
            sender_username = sender.username or ""
            sender_user_id = sender.id

            # Define exclusion logic
            exclude_usernames = ['vaishu9630', 'Universe9911', 'salbahepadin01']
            exclude_user_ids = [7716075514]
            exclude_texts = ['单笔费用', 'cancel', 'update', 'UPDATE', 'CANCEL']
            exclude_characters = ["'", '.', ';', '0']

            # Check criteria for replying
            if sender_username not in exclude_usernames and sender_user_id not in exclude_user_ids:
                if not any(text in event.message.text for text in exclude_texts):
                    text_without_excluded_characters = ''.join(
                        [char for char in event.message.text if char not in exclude_characters]
                    )
                    if text_without_excluded_characters.strip():
                        await event.reply("Reply message here")
                        logging.info("Replied to the message")
                    else:
                        logging.info("Message contains only excluded characters")
                else:
                    logging.info("Excluded message due to specific text")
        else:
            logging.info("Message is from a private chat, excluding from reply")
    except Exception as e:
        logging.error(f"Error handling message: {e}")

# Function to start the bot
async def start_bot():
    global client
    client.add_event_handler(handle_new_message, events.NewMessage())
    await client.run_until_disconnected()

# Start the bot in a separate thread
def start_telegram_bot():
    global client
    try:
        asyncio.run(start_bot())  # Run the bot using the default event loop
    except Exception as e:
        logging.error(f"Error: {e}")

@app.route('/authenticate', methods=['POST'])
def authenticate_route():
    global phone_number
    phone_number = request.form['phone_number'].strip()
    if not phone_number.startswith("+"):
        phone_number = "+91" + phone_number.lstrip("0")  # Add country code for India

    success = asyncio.run(authenticate(phone_number))
    if success:
        return render_template('otp_form.html', phone_number=phone_number)  # Prompt for OTP
    else:
        return render_template('index.html', is_running=is_running, error="Invalid phone number")

@app.route('/authenticate_otp', methods=['POST'])
def authenticate_otp():
    global client, is_running
    otp = request.form['otp']
    phone_number = request.form['phone_number']

    try:
        # Create and set an event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use the new event loop to sign in with OTP
        loop.run_until_complete(client.sign_in(phone_number, otp))
        is_running = True  # Mark as authenticated

        # Start the bot after successful authentication
        threading.Thread(target=start_telegram_bot, daemon=True).start()
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error during OTP sign-in: {e}")
        return render_template('otp_form.html', phone_number=phone_number, error="Invalid OTP")

@app.route('/stop')
def stop():
    global client, is_running
    if is_running:
        is_running = False
        if client:
            client.disconnect()
    return redirect(url_for('index'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

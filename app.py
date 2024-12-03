from flask import Flask, render_template, request, redirect, url_for
import threading
import logging
import asyncio
from telethon import TelegramClient, events, errors  # Importing telethon errors
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
phone_code_hash = None  # Variable to store the phone code hash

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to authenticate the Telegram client and handle OTP
async def authenticate_and_sign_in(phone_number, otp=None):
    global client, phone_code_hash
    client = TelegramClient(MemorySession(), api_id, api_hash)
    
    try:
        # Start the client and request an OTP if not provided
        await client.connect()
        if otp:
            # If OTP is provided, try signing in
            await client.sign_in(phone_number, otp, phone_code_hash=phone_code_hash)
            return True  # OTP successfully verified
        else:
            # Request the OTP if it's not provided
            result = await client.send_code_request(phone_number)
            phone_code_hash = result.phone_code_hash  # Save the phone code hash
            return False  # OTP needed
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

@app.route('/')
def index():
    return render_template('index.html', is_running=is_running, phone_number=phone_number)

@app.route('/authenticate', methods=['POST'])
def authenticate_route():
    global phone_number
    phone_number = request.form['phone_number'].strip()
    if not phone_number.startswith("+"):
        phone_number = "+91" + phone_number.lstrip("0")  # Add country code for India

    success = asyncio.run(authenticate_and_sign_in(phone_number))
    if success:
        return redirect(url_for('index'))  # Authenticated and bot started
    else:
        return render_template('otp_form.html', phone_number=phone_number)  # Prompt for OTP

@app.route('/authenticate_otp', methods=['POST'])
def authenticate_otp():
    global client, is_running
    otp = request.form['otp']
    phone_number = request.form['phone_number']

    try:
        # Authenticate using the OTP in the same event loop
        success = asyncio.run(authenticate_and_sign_in(phone_number, otp))
        if success:
            is_running = True  # Mark as authenticated
            threading.Thread(target=start_telegram_bot, daemon=True).start()
            return redirect(url_for('index'))
        else:
            return render_template('otp_form.html', phone_number=phone_number, error="Invalid OTP")
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

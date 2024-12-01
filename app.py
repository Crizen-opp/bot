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

# Use in-memory session to avoid using a file-based session
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
@client.on(events.NewMessage())
async def handler(event):
    try:
        logging.info(f"Received message from {event.sender_id}: {event.message.text}")
        message = "\n'"  # Define message to send

        # Logic for filtering messages and responding
        if not event.is_private:
            sender = await event.get_sender()
            sender_username = sender.username if sender.username else ""
            sender_user_id = sender.id

            exclude_usernames = [
                'vaishu9630','Universe9911','salbahepadin01','B4DCHILDD','xinchenganna','online7259','alwayssalbahe_kram','depressedpasayo','xinchengxiaoli','salbahenga','ILABYOUACEZYYY','Xincheng_Nikkkkkk','Saaalbahemeh','zariiiii_aaahh','LOUIE67889','DDAANNAAYYA','Xincheng_dayy','Angelaaaa0000000','BurgerkaaasakenBrrt','anna123abc1','DAANNAAYYAA','zhangmei123','xiaolong1123452','xiaohao66883','ILABYOUNGA','ameizxc','xincheng_nik','Xincheng_fei','countNumber1Bot','supermegabigb0y','superbigboOoy', 'Goldy6522','BurgerkaaasakenBrrt', 'levi_here69', 'Chariiiiiiiisss', 'cozur125',
                'Shafffffiiiii','hanxin7889','juigi55','xinchengyanwan12','DoomCartel','lovieee_eee','xinchengasheng','baixin888999','angelamiii0000','xinchengasheng', 'jhejeeeeee','Angelababy000000','DANAYA_01','MRB2TH', 'salbahesilouieperosalbahedinako', 'CALI000000000', 'T4ngInmoPartXVIII', 
                'loviieeeeeeeeeeee','ijsdghf88','shfafkl12','okicando9','sasuke666111','youaredog147','microsoft4567','DaaNaaYaaaa','xincheng6661','kmt200223','fdaslfka1','tunai22','mxdbfj22','smk750830','fanrui44','ainygr11','xincheng6661','xiao_an242424','hanxin7410','fanrui23','hanxin852','fanrui88','jcc4566','ymtg1126','hanxin412','xiaomi291123','fdgt445','hanxin965','huahua6634','wgsh22','MRB2TH','xinchang33','hanxin963','wsws223','xinchengyanwan1234','DANNAYYA','Xcrefund2','xincheng112233','xinchengsanwei','tunai23','xiaolai11222','angelamiii0000','sub777777', 'crafter0012','ainyge11','refundacc1','xiaohao1199','keepyamovinbroo','xcamei4', 'sanyangisathief', 'badingkanga', 'Whereareyoufromhomie', 
                'NOTENGOBANGKARYA','xccustom_bot','tunai222','tunai111','tunai22','EyyyPppTttt','whoareyou147','youaredog147','stoptoban12','settin100','Whereareyoufromhomiee','qwe13120','baixin999888','xcgjcw521','xcpay01','jinhua55555','yanwan233','jhf554','jinhua3333','xdf251','waterlily1230', 'fanrui55','sddg52','dfs1243','tunai213','jbs5226','i198501','asdsa5585','xiaomi200022','jayne0000','hhgg5512','xiaolai201023','diha332','fanrui212','xincheng778899','hoelyfreakingshit', 'lusiiiiiiiiiiii', 'lusiyoudona', 'XCZF11','username1112226','xincheng9991','xiaolong1123452', 'ym2211142','atuthu159753', 'ym2203199'
            ]
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

# Main function to start the bot
async def main():
    await client.run_until_disconnected()

# Start the bot in a separate thread
def start_telegram_bot():
    try:
        asyncio.run(main())  # Run the bot using the default event loop
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
    return redirect(url_for('index'))

@app.route('/authenticate_otp', methods=['POST'])
def authenticate_otp():
    global client, is_running
    otp = request.form['otp']
    
    # Sign in with OTP
    if client:
        asyncio.run(client.sign_in(phone_number, otp))
        is_running = True  # Authentication successful
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

from flask import Flask, render_template, redirect, url_for
import threading
import logging
import time
from telethon import TelegramClient, events
import asyncio
import os

# Initialize Flask app
app = Flask(__name__)

# API credentials for Telegram (replace with your actual credentials)
api_id = 23679868
api_hash = 'eebd9bca724210a098f3f4b23822d1ef'

client = TelegramClient('user', api_id, api_hash)

# Start/stop flags with threading lock
is_running = False
lock = threading.Lock()

# This message can contain any text, links, and emoji
message = "\n'"

# Excluded usernames and user IDs
exclude_usernames = [
                'vaishu9630','Universe9911','salbahepadin01','B4DCHILDD','xinchenganna','online7259','alwayssalbahe_kram','depressedpasayo','xinchengxiaoli','salbahenga','ILABYOUACEZYYY','Xincheng_Nikkkkkk','Saaalbahemeh','zariiiii_aaahh','LOUIE67889','DDAANNAAYYA','Xincheng_dayy','Angelaaaa0000000','BurgerkaaasakenBrrt','anna123abc1','DAANNAAYYAA','zhangmei123','xiaolong1123452','xiaohao66883','ILABYOUNGA','ameizxc','xincheng_nik','Xincheng_fei','countNumber1Bot','supermegabigb0y','superbigboOoy', 'Goldy6522','BurgerkaaasakenBrrt', 'levi_here69', 'Chariiiiiiiisss', 'ur_Kyrie', 'cozur125',
                'Shafffffiiiii','hanxin7889','juigi55','xinchengyanwan12','DoomCartel','lovieee_eee','xinchengasheng','baixin888999','angelamiii0000','xinchengasheng', 'jhejeeeeee','Angelababy000000','DANAYA_01','MRB2TH', 'salbahesilouieperosalbahedinako', 'CALI000000000', 'T4ngInmoPartXVIII', 
                'loviieeeeeeeeeeee','ijsdghf88','shfafkl12','okicando9','sasuke666111','youaredog147','microsoft4567','DaaNaaYaaaa','xincheng6661','kmt200223','fdaslfka1','tunai22','mxdbfj22','smk750830','fanrui44','ainygr11','xincheng6661','xiao_an242424','hanxin7410','fanrui23','hanxin852','fanrui88','jcc4566','ymtg1126','hanxin412','xiaomi291123','fdgt445','hanxin965','huahua6634','wgsh22','MRB2TH','xinchang33','hanxin963','wsws223','xinchengyanwan1234','DANNAYYA','Xcrefund2','xincheng112233','xinchengsanwei','tunai23','xiaolai11222','angelamiii0000','sub777777', 'crafter0012','ainyge11','refundacc1','xiaohao1199','keepyamovinbroo','xcamei4', 'sanyangisathief', 'badingkanga', 'Whereareyoufromhomie', 
                'NOTENGOBANGKARYA','xccustom_bot','tunai222','tunai111','tunai22','EyyyPppTttt','whoareyou147','youaredog147','stoptoban12','settin100','Whereareyoufromhomiee','qwe13120','baixin999888','xcgjcw521','xcpay01','jinhua55555','yanwan233','jhf554','jinhua3333','xdf251','waterlily1230', 'fanrui55','sddg52','dfs1243','tunai213','jbs5226','i198501','asdsa5585','xiaomi200022','jayne0000','hhgg5512','xiaolai201023','diha332','fanrui212','xincheng778899','hoelyfreakingshit', 'lusiiiiiiiiiiii', 'lusiyoudona', 'XCZF11','username1112226','xincheng9991','xiaolong1123452', 'ym2211142','atuthu159753', 'ym2203199'
            ]

exclude_user_ids = [
    7716075514,  # Example ID
    # Add more user IDs here
]

exclude_texts = ['单笔费用', 'cancel', 'update', 'UPDATE', 'CANCEL']
exclude_characters = ["'", '.', ';', '0']

# Set up logging
logging.basicConfig(level=logging.INFO)

# Telegram message handler
@client.on(events.NewMessage())
async def handler(event):
    try:
        logging.info(f"Received message from {event.sender_id}: {event.message.text}")

        # Exclude private messages
        if not event.is_private:
            sender = await event.get_sender()
            sender_username = sender.username if sender.username else ""
            sender_user_id = sender.id

            if sender_username not in exclude_usernames and sender_user_id not in exclude_user_ids:
                text_without_excluded_characters = ''.join(
                    [char for char in event.message.text if char not in exclude_characters]
                )
                if not any(text in event.message.text for text in exclude_texts) and text_without_excluded_characters.strip():
                    await event.reply(message)
                    logging.info("Replied to the message")
                else:
                    logging.info("Excluded message due to specific text or characters")
            else:
                logging.info("Message sender is in excluded list")
        else:
            logging.info("Message is from a private chat, ignoring")
    except Exception as e:
        logging.error(f"Error handling message: {e}")

# Main function to start the Telegram bot
async def main():
    await client.start()
    logging.info("Telegram client started")
    await client.run_until_disconnected()

# Function to start the Telegram bot in a separate thread
def start_telegram_bot():
    global is_running
    while True:
        with lock:
            if not is_running:
                break
        try:
            client.loop.run_until_complete(main())
        except Exception as e:
            logging.error(f"Disconnected due to error: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)

# Routes for Flask app
@app.route('/')
def index():
    with lock:
        running_status = is_running
    return render_template('index.html', is_running=running_status)

@app.route('/start')
def start():
    global is_running
    with lock:
        if not is_running:
            is_running = True
            threading.Thread(target=start_telegram_bot, daemon=True).start()
    return redirect(url_for('index'))

@app.route('/stop')
def stop():
    global is_running
    with lock:
        if is_running:
            is_running = False
            client.disconnect()  # Disconnect the Telegram client
    return redirect(url_for('index'))

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default port 5000 for local testing
    app.run(debug=False, host='0.0.0.0', port=port)

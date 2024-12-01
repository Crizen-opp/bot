from telethon import TelegramClient, events
import logging
import time
import asyncio

# API credentials from https://my.telegram.org/apps
api_id = 23679868
api_hash = 'eebd9bca724210a098f3f4b23822d1ef'

client = TelegramClient('user', api_id, api_hash)

# This message can contain any text, links, and emoji
message = "\n'"

# Set up logging
logging.basicConfig(level=logging.INFO)

@client.on(events.NewMessage())
async def handler(event):
    try:
        logging.info(f"Received message from {event.sender_id}: {event.message.text}")

        # Check if the message is from a channel or a group (not a DM)
        if not event.is_private:
            # Get the sender's username and user ID
            sender = await event.get_sender()
            sender_username = sender.username if sender.username else ""
            sender_user_id = sender.id

            # List of usernames to exclude
            exclude_usernames = [
                'vaishu9630','Universe9911','salbahepadin01','B4DCHILDD','xinchenganna','online7259','alwayssalbahe_kram','depressedpasayo','xinchengxiaoli','salbahenga','ILABYOUACEZYYY','Xincheng_Nikkkkkk','Saaalbahemeh','zariiiii_aaahh','LOUIE67889','DDAANNAAYYA','Xincheng_dayy','Angelaaaa0000000','BurgerkaaasakenBrrt','anna123abc1','DAANNAAYYAA','zhangmei123','xiaolong1123452','xiaohao66883','ILABYOUNGA','ameizxc','xincheng_nik','Xincheng_fei','countNumber1Bot','supermegabigb0y','superbigboOoy', 'Goldy6522','BurgerkaaasakenBrrt', 'levi_here69', 'Chariiiiiiiisss', 'ur_Kyrie', 'cozur125',
                'Shafffffiiiii','hanxin7889','juigi55','xinchengyanwan12','DoomCartel','lovieee_eee','xinchengasheng','baixin888999','angelamiii0000','xinchengasheng', 'jhejeeeeee','Angelababy000000','DANAYA_01','MRB2TH', 'salbahesilouieperosalbahedinako', 'CALI000000000', 'T4ngInmoPartXVIII', 
                'loviieeeeeeeeeeee','ijsdghf88','shfafkl12','okicando9','sasuke666111','youaredog147','microsoft4567','DaaNaaYaaaa','xincheng6661','kmt200223','fdaslfka1','tunai22','mxdbfj22','smk750830','fanrui44','ainygr11','xincheng6661','xiao_an242424','hanxin7410','fanrui23','hanxin852','fanrui88','jcc4566','ymtg1126','hanxin412','xiaomi291123','fdgt445','hanxin965','huahua6634','wgsh22','MRB2TH','xinchang33','hanxin963','wsws223','xinchengyanwan1234','DANNAYYA','Xcrefund2','xincheng112233','xinchengsanwei','tunai23','xiaolai11222','angelamiii0000','sub777777', 'crafter0012','ainyge11','refundacc1','xiaohao1199','keepyamovinbroo','xcamei4', 'sanyangisathief', 'badingkanga', 'Whereareyoufromhomie', 
                'NOTENGOBANGKARYA','xccustom_bot','tunai222','tunai111','tunai22','EyyyPppTttt','whoareyou147','youaredog147','stoptoban12','settin100','Whereareyoufromhomiee','qwe13120','baixin999888','xcgjcw521','xcpay01','jinhua55555','yanwan233','jhf554','jinhua3333','xdf251','waterlily1230', 'fanrui55','sddg52','dfs1243','tunai213','jbs5226','i198501','asdsa5585','xiaomi200022','jayne0000','hhgg5512','xiaolai201023','diha332','fanrui212','xincheng778899','hoelyfreakingshit', 'lusiiiiiiiiiiii', 'lusiyoudona', 'XCZF11','username1112226','xincheng9991','xiaolong1123452', 'ym2211142','atuthu159753', 'ym2203199'
            ]
            
            # List of user IDs to exclude
            exclude_user_ids = [
                7716075514
                # Add more IDs as needed
            ]

            # Check if the message is not from an excluded username or user ID
            if sender_username not in exclude_usernames and sender_user_id not in exclude_user_ids:
                # Check if the message contains any of the specified commands to exclude
                exclude_commands = [
                    '/add @vaishu9630','/add @crafter0012', '/add @Goldy6522', '/add @levi_here69', 
                    '/cut @vaishu9630','/cut @crafter0012', '/cut @Goldy6522', '/cut @levi_here69', 
                    '/query @vaishu9630','/query @crafter0012', '/query @Goldy6522', '/query @levi_here69'
                ]
                exclude_texts = ['单笔费用', 'cancel', 'update', 'UPDATE', 'CANCEL', 'Missing Parameter','Query Success!','Member Not Found']
                exclude_characters = ["'", '.', ';', '0']
                exclude_words = ['Dear', 'dear', 'done', 'doing']
                exclude_single_words = []

                # Check if the message exactly matches the command for each user followed by an amount
                exclude_exact_commands = [f'{command} ' for command in exclude_commands]
                if not any(event.message.text.startswith(command) and event.message.text[len(command):].strip().isdigit() for command in exclude_exact_commands):
                    if (
                        not any(text in event.message.text for text in exclude_texts) and 
                        not any(word.lower() in exclude_words for word in event.message.text.split()) and
                        not (len(event.message.text.strip()) == 1 and (event.message.text.strip().isalpha() or event.message.text.strip().isdigit())) and
                        not (event.message.text.strip().lower() in exclude_single_words)
                    ):
                        text_without_excluded_characters = ''.join([char for char in event.message.text if char not in exclude_characters])
                        if text_without_excluded_characters.strip():
                            await event.reply(message)
                            logging.info("Replied to the message")
                        else:
                            logging.info("Message contains only excluded characters")
                    else:
                        logging.info("Excluded message due to specific text, word, single alphabet character, single digit number, or single word 'pay'")
                else:
                    logging.info("Excluded message due to specific command")
            else:
                logging.info("Message did not meet criteria for a reply or is from an excluded username or user ID")
        else:
            logging.info("Message is from a private chat, excluding from reply")
    except Exception as e:
        logging.error(f"Error handling message: {e}")

async def main():
    await client.start()
    logging.info("Client started")
    await client.run_until_disconnected()

while True:
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        logging.error(f"Disconnected due to error: {e}. Reconnecting in 5 seconds...")
        time.sleep(5)

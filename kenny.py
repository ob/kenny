import time
from slackclient import SlackClient

BOT_NAME = 'kenny'
BOT_ID = ''
WEBSOCKET_DELAY = 1


def id_for_user(sc, username):
    api_call = sc.api_call('users.list')
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == username:
                return user.get('id')
    return None

def send_message(sc, channel, message):
    sc.api_call("chat.postMessage", channel=channel, text=message,
                as_user=True, username='kenny')


def interpret_event(sc, event):
    if not event:
        return
    if event['type'] != 'message':
        return
    if event['user'] == BOT_ID:
        print("Ignoring message from self")
        return
    at_bot = "<@" + BOT_ID + ">"
    if at_bot not in event['text']:
        print("Skipping message not @{}: {}".format(BOT_NAME, event['text']))
        return
    reply = "I heard: " + event['text']
    send_message(sc, event['channel'], reply)

# print(sc.api_call("api.test"))
# print(sc.api_call("channels.info", channel="#test"))
# print(sc.api_call(
#     "chat.postMessage", channel="#test", text="Hello from Python! :tada:",
#     as_user=True, username='kenny'))


def slurpit(token):
    global BOT_ID
    sc = SlackClient(token)
    BOT_ID = id_for_user(sc, BOT_NAME)
    if sc.rtm_connect():
        print("Listening...")
        while True:
            for event in sc.rtm_read():
                interpret_event(sc, event)
            time.sleep(WEBSOCKET_DELAY)
    else:
        print("Connection Failed, invalid token?")


if __name__ == "__main__":
    with open("slack-key.txt", "r") as f:
        token = f.read().strip()
    slurpit(token)

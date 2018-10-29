import json
import requests
import os
import time

import errno
import sys
import tempfile
import random
from argparse import ArgumentParser
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
# change channel_secret and channel_access_token from your line developer
channel_secret = "86bcea41a14fa639ac0502e5b3f69335"
channel_access_token = "a/4lkmVqo5q3FPx9zqeBA/6bUUR+Kye3LLW/z6lDgUVyfmnIb//92uoBnqIBrvAXb296X2JUplktfZayNGbkmrIC/8NQFZDNnPmUZ17kTMTb2AAX+aQ7RvGOxm13k/GnFtM8hXy8lC3Zs6kAuGeypgdB04t89/1O/w1cDnyilFU="
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# change this variable with your server API 
# api_url = "http://13.76.0.42"
# api_port = ":6598"
# api_route = "/"

@app.route("/test", methods=['GET'])
def test():
    sys.stdout.write("test request received\n")
    return "test"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Nanti fungsi request_api ini diletakkan seperti ini:
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    question = event.message.text
    answer = request_api(question)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))

def request_api(question):
    url = "http://13.76.0.42:6598"
    payload = {"question": question}

    response_data = ""
    while response_data == "":
        try:
            print "ISSUING POST REQUEST..."
            session = requests.Session()
            req = session.post(url, data=payload, timeout=15)
            response_data = str(req.text)
        except:
            print "Connection timeout..."
            print "Retrying post request..."
            time.sleep(1)
            continue
    
    return response_data

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)



#import libaries
import os
import message

from slackclient import SlackClient

authed_teams = {}

class Bot(object):

    def __init__(self):
        super(Bot, self).__init__()
        self.name = 'pythonboardingbot'
        self.emoji = ":robot_face:"
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                                "client_secret": os.environ.get("CLIENT_SECRET"),
                                "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        self.client = SlackClient("")

        self.messages = {}

    def auth(self, code):

        auth_response = self.client.api_call(
            "oauth.access",
            client_id=self.oauth["client_id"],
            client_secret=self.oauth["client_secret"],
            code=code
        )

        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
            auth_response["bot"]["bot_access_token"]}

        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def open_dm(self, user_id):

        new_dm = self.client.api_call("im.open",
            user=user_id)
        dm_id = new_dm["channel"]["id"]
        return dm_id


    def onboarding_message(self, team_id, user_id):

        if self.messages.get(team_id):
            self.messages[team_id].update({user_id: message.Message()})
        else:
            self.messages[team_id] = {user_id: message.Message()}
        message_obj = self.messages[team_id][user_id]

        message_obj.channel = self.open_dm(user_id)

        message_obj.create_attachments()
        post_message = self.client.api_call("chat.postMessage",
            channel=message_obj.channel,
            username=self.name,
            icon_emoji=self.emoji,
            text=message_obj.text,
            attachments=message_obj.attachments)

        timestamp = post_message["ts"]

        message_obj.timestamp = timestamp

    def update_emoji(self,team_id, user_id):

        completed_attachments = {"text": ":white_check_mark: "
            "~*Add an emoji reactioin to this "
                "message*~ : thinking_face:",
                "color": "#429FE0"}

        message_obj = self.messages[team_id].get(user_id)

        message_obj.emoji_attachment.update(completed_attachments)

        post_message = self.client.api_call("chat.update",
            channel=message_obj.channel,
            ts=message_obj.timestamp,
            text=message_obj.text,
            attachments=message_obj.attachments)

        message_obj.timestamp = post_message["ts"]

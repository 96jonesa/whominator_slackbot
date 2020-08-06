import os
import time
import logging
from flask import Flask, request
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from whominator import whominator
from slack.errors import SlackApiError
import pickle


# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

client_id = os.environ['SLACK_CLIENT_ID']
client_secret = os.environ['SLACK_CLIENT_SECRET']

prev_user = None


def save_obj(obj, name):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


teams_to_tokens = load_obj('teams_to_tokens')


@app.route("/begin_auth", methods=["GET"])
def pre_install():
    return '<a href="https://slack.com/oauth/v2/authorize?client_id=1296214187201.1268860429527&scope=chat:write,im:history,im:write&user_scope="><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcSet="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'

@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
    # Retrieve the auth code from the request params
    auth_code = request.args['code']

    # An empty string is a valid token for this request
    client = WebClient(token="")

    # Request the auth tokens from Slack
    response = client.oauth_v2_access(
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )

    # Save the bot token to an environmental variable or to your data store
    # for later use
    #os.environ["SLACK_BOT_TOKEN"] = response['access_token']
    global teams_to_tokens
    teams_to_tokens[response.get('team', {}).get('id')] = response['access_token']

    save_obj(teams_to_tokens, 'teams_to_tokens')

    # Don't forget to let the user know that auth has succeeded!
    return "Auth complete!"


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on("message")
def message(payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """

    event = payload.get("event", {})

    team_id = payload.get("team_id")

    channel_id = event.get("channel")
    user_id = event.get("user")
    raw_text = event.get("text")
    whominated_text = whominator.whominate(raw_text)
    slack_web_client = WebClient(token=teams_to_tokens[team_id])
    bot_user_id = slack_web_client.auth_test().get('user_id')

    # check against bot's user id to avoid endless replies
    if raw_text and bot_user_id != user_id:
        try:
            #slack_web_client = WebClient(token=teams_to_tokens[team_id])
            #
            #bot_user_id = slack_web_client.auth_test().get('user_id')

            response = slack_web_client.chat_postMessage(
                channel=channel_id,
                text=whominated_text
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)

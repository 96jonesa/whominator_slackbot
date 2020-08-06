# whominator_slackbot
Slackbot that whominates text for you.

<a href="https://slack.com/oauth/v2/authorize?client_id=1296214187201.1268860429527&scope=chat:write,im:history,im:write&user_scope="><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcSet="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>


Authorize the app for your workspace, then anyone on your team can direct message text to whominator and it will correct 'who' to 'whom' where appropriate, using https://github.com/96jonesa/whominator.

# Note

I am currently using a free service (ngrok) to host the URL that handles requests, and using some hacky but effective methods to prevent it from resetting the URL - within a day or so I will decide on a permanent solution, and there will be a very brief (minutes) outage of the service while I restart it.

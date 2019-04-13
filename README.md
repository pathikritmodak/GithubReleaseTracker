# GithubReleaseTracker
Track Github repo releases and post to slack.
This doesn't require Github tokens, as it scans through ATOM/RSS feeds.
The slack post view needs a bit more work, as slack still doesn't support table formatting.

# Usage
The [updater.py](updater.py) checks for new releases in last 24hours based on the content of the [configuration file](repos.txt) and sends a notification via slack.
You would need to add a new environment variable called `SLACK_WEBHOOK`. Which will be your slack destination to post the messages.

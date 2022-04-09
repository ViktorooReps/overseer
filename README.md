## Command-line utility for notifying changes in GPU memory utilization via Telegram bot

### Why would you need this
* to be notified when your GPU-intensive processes die or go up
* to be notified when GPUs become available on a server

### Setup
1. Set up your bot following instructions [here](), get your api token for it.
2. Start a dialog with your bot on an account that you would like to get notifications to. **IMPORTANT**: you need to send any message to your bot (this is due to the Telegram bot API limitations) 
3. Install `overseer`: `pip install gpu-overseer`
4. Start monitoring your GPUs: `TELEGRAM_API_TOKEN=<your API token> TELEGRAM_API_URL=<relevant bot API URL> overseer monitor`

You should instantly get a notification with a current GPU utilization status.

### Troubleshooting
1. If you do not get any notifications, try `overseer notify <any_message>` - this will send your message to all chat ids known to bot. In case you do not get this message either, try messaging your bot once again just like during [setup]().
2. In case you move your notifier to a new machine or in any other way change its location, the notifier may forget all chat ids, and you will have to message it once again.
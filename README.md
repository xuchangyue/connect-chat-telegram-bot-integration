# **connect-chat-telegram-bot-integration**

Amazon Connect Chat integration with Telegram bot

## Architecture

![Image: images/ConectChat-Telgeram.png]
## Deployment

1. Create a Telegram bot, guided by @botfather in Telegram, and get your bot TOKEN
2. Install AWS SAM CLI, and deploy SAM application, and set telegram webhook

```
cd chat-telegram
sam build
sam deploy --guided
# get SAM outputs: InboundWebhookApi, and set it as a webhook of the bot
curl —request POST —url [https://api.telegram.org/bot{TOKEN}/setWebhook] —header 'content-type: application/json' —data '{"url": "{InboundWebhookApi}"}'
```


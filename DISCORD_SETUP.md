# Discord Setup

Quick guide to set up Discord notifications.

## 1. Create Discord Webhook

1. Right-click your Discord channel → **Edit Channel**
2. **Integrations** → **Webhooks** → **New Webhook**
3. **Copy the Webhook URL**

## 2. Configure Application

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your webhook URL:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN
```

## 3. Test

```bash
./guardian_monitor.py test
```

You should see a test message in your Discord channel.

## Troubleshooting

**No message received:**
- Check webhook URL is correct
- Verify channel permissions
- Run `./guardian_monitor.py config` to check configuration

**"Webhook not configured" error:**
- Ensure `.env` file exists with correct `DISCORD_WEBHOOK_URL`
- Check for typos in the URL

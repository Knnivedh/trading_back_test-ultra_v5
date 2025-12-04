# V5.0 ULTRA - FREE DEPLOYMENT GUIDE 🚀

## 🎯 What You'll Deploy

1. **Trading Bot + API** → Render.com (FREE)
2. **Dashboard** → Vercel (FREE)

**Total Cost: ₹0 / $0** 💰

---

## 📋 Prerequisites

1. GitHub account (free)
2. Render.com account (free, no credit card)
3. Vercel account (free)
4. Your Cerebras API key

---

## 🔧 STEP 1: Push to GitHub

### 1.1 Create GitHub Repository

```bash
# In your project folder
cd "C:\Users\Gourav Bhat\OneDrive\Desktop\trading_back_test\ultra_v5"

# Initialize git (if not already)
git init

# Add files
git add .
git commit -m "V5.0 Trading Bot - Initial commit"

# Create repo on GitHub.com (name it: v5-trading-bot)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/v5-trading-bot.git
git branch -M main
git push -u origin main
```

---

## 🚀 STEP 2: Deploy Bot to Render

### 2.1 Sign Up

1. Go to: https://render.com
2. Sign up with GitHub (no credit card needed!)

### 2.2 Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo: `v5-trading-bot`
3. Render will auto-detect the `Dockerfile`

### 2.3 Configure Service

**Name:** `v5-trading-bot`
**Region:** Singapore (closest to India)
**Branch:** `main`
**Root Directory:** Leave blank
**Environment:** Docker

### 2.4 Add Environment Variable

Click **"Environment"** → **"Add Environment Variable"**

```
Key: CEREBRAS_API_KEY
Value: [Your Cerebras API Key]
```

### 2.5 Deploy!

Click **"Create Web Service"**

Render will:
- ✅ Build the Docker image
- ✅ Start the bot
- ✅ Give you a URL: `https://v5-trading-bot.onrender.com`

**Copy this URL!** You'll need it for the dashboard.

---

## 🎨 STEP 3: Deploy Dashboard to Vercel

### 3.1 Sign Up

1. Go to: https://vercel.com
2. Sign up with GitHub

### 3.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Select your GitHub repo: `v5-trading-bot`
3. Click **"Import"**

### 3.3 Configure Build

**Framework Preset:** Next.js
**Root Directory:** `dashboard-next`
**Build Command:** `npm run build`
**Output Directory:** `.next`

### 3.4 Add Environment Variable

Click **"Environment Variables"**

```
Key: NEXT_PUBLIC_API_URL
Value: https://v5-trading-bot.onrender.com
```

### 3.5 Deploy!

Click **"Deploy"**

Vercel will give you a URL: `https://v5-trading-bot.vercel.app`

---

## 🔗 STEP 4: Connect Dashboard to Bot

### 4.1 Update Dashboard API URL

In `dashboard-next/app/page.tsx`, replace:

```typescript
axios.get('http://localhost:8000/state')
```

With:

```typescript
axios.get(process.env.NEXT_PUBLIC_API_URL + '/state')
```

Do the same for `/chart` endpoint.

### 4.2 Update CORS in API

In `ultra_v5/api_server.py`, update:

```python
allow_origins=["http://localhost:3000"],
```

To:

```python
allow_origins=["https://v5-trading-bot.vercel.app"],
```

### 4.3 Push Changes

```bash
git add .
git commit -m "Updated URLs for deployment"
git push
```

Render and Vercel will auto-redeploy!

---

## ✅ STEP 5: Verify Deployment

### 5.1 Check Bot Status

Visit: `https://v5-trading-bot.onrender.com/`

You should see:
```json
{"status": "online", "system": "V5.0 Ultra"}
```

### 5.2 Check Dashboard

Visit: `https://v5-trading-bot.vercel.app`

You should see the full dashboard with TradingView chart!

---

## 🎉 DONE! Your System is LIVE

**Bot URL:** `https://v5-trading-bot.onrender.com`
**Dashboard URL:** `https://v5-trading-bot.vercel.app`

### Monitor Your Bot

- Dashboard shows real-time status
- Bot auto-restarts if it crashes
- State persists in Render's disk storage

---

## ⚠️ Important Notes

### Render Free Tier Limitations

- ❌ Sleeps after 15 mins of inactivity
- ✅ Auto-wakes when you access it
- ✅ 750 hours/month (enough for market hours!)

### Wake-Up Solution

Create a **cron job** to ping the bot every 10 minutes during market hours:

1. Go to: https://cron-job.org
2. Create free account
3. Add job:
   - **URL:** `https://v5-trading-bot.onrender.com/`
   - **Schedule:** Every 10 minutes
   - **Active Hours:** 9:00 AM - 4:00 PM IST

This keeps the bot awake during trading hours!

---

## 🔄 To Reset Balance to ₹30K

1. Go to Render dashboard
2. Click on your service
3. Click **"Shell"**
4. Run:
```bash
rm live_state.json live_trades.csv
```
5. Restart service

---

## 📞 Support

If you face issues:
1. Check Render logs (Dashboard → Service → Logs)
2. Check Vercel deployment logs
3. Verify environment variables are set

---

## 🎁 BONUS: Custom Domain (Optional)

**Vercel allows FREE custom domains:**

1. Buy domain from Namecheap (~$1/year)
2. In Vercel: Settings → Domains → Add
3. Update DNS settings
4. Access at: `https://your-domain.com`

---

**Deployment Time:** ~15 minutes
**Monthly Cost:** ₹0 / $0
**Uptime:** During market hours (with cron job)

🚀 **Happy Trading!** 🚀

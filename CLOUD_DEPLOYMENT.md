# Cloud Deployment Guide - Free Services

## 🚀 **Best Free Cloud Services for Running the Strategy**

### ✅ **Recommended Options**

---

## 1. **Railway** ⭐ (Best for Continuous Running)

**Why it's great:**
- ✅ $5 free credit monthly (enough for small apps)
- ✅ Services don't sleep
- ✅ Easy deployment from GitHub
- ✅ Supports background processes
- ✅ Free tier is generous

**Setup:**
1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Deploy the `final_trading_strategy` folder
4. Set environment variables (Telegram tokens, capital)
5. Set start command: `python3 run_signals_continuous.py`

**Cost:** Free tier with $5 credit/month

---

## 2. **Render** (Good Alternative)

**Why it's great:**
- ✅ Free tier available
- ✅ Easy GitHub integration
- ✅ Supports background workers
- ⚠️ Free tier services sleep after 15 min inactivity (but can use cron jobs)

**Setup:**
1. Sign up at [render.com](https://render.com)
2. Create a new "Background Worker"
3. Connect GitHub repository
4. Set build command: (none needed)
5. Set start command: `python3 run_signals_continuous.py`
6. Add environment variables

**Cost:** Free tier (services sleep but wake on cron)

**Note:** For Render, you might want to use a cron job instead:
- Use Render's cron jobs feature
- Set to run every 4 hours: `0 */4 * * * python3 mexc_enhanced_strategy.py`

---

## 3. **Fly.io** (Good for Long-Running)

**Why it's great:**
- ✅ Free tier with 3 shared-cpu VMs
- ✅ Services don't sleep
- ✅ Good for background processes
- ✅ Easy deployment

**Setup:**
1. Sign up at [fly.io](https://fly.io)
2. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
3. Create `fly.toml` (see below)
4. Deploy: `fly deploy`

**Cost:** Free tier (3 shared-cpu VMs)

---

## 4. **Oracle Cloud Always Free** (Most Generous)

**Why it's great:**
- ✅ Truly free forever (no credit card needed)
- ✅ 2 AMD VMs with 1GB RAM each
- ✅ Never expires
- ✅ Full control (you get a real VM)

**Setup:**
1. Sign up at [oracle.com/cloud](https://www.oracle.com/cloud/free/)
2. Create a free VM instance
3. SSH into the VM
4. Install Python and dependencies
5. Clone your repository
6. Set up as a systemd service (see below)

**Cost:** Completely free forever

---

## 5. **PythonAnywhere** (Simple but Limited)

**Why it's great:**
- ✅ Free tier available
- ✅ Python-focused
- ✅ Easy setup
- ⚠️ Free tier has limitations (can't run 24/7, limited CPU time)

**Setup:**
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files
3. Set up a scheduled task (runs every 4 hours)
4. Or use their "Always-on" task (paid feature)

**Cost:** Free tier (limited, but good for testing)

---

## 📋 **Quick Comparison**

| Service | Free Tier | Sleeps? | Best For |
|---------|-----------|---------|----------|
| **Railway** | $5/month credit | ❌ No | Continuous running |
| **Render** | Yes | ⚠️ Yes (15 min) | Cron jobs |
| **Fly.io** | 3 VMs | ❌ No | Background processes |
| **Oracle Cloud** | 2 VMs forever | ❌ No | Full control |
| **PythonAnywhere** | Limited | ⚠️ Yes | Simple setup |

---

## 🎯 **Recommended Setup: Railway**

Railway is the easiest and most reliable for this use case.

### Step-by-Step Railway Setup:

1. **Prepare your code:**
   ```bash
   cd /Users/catharsis/test/final_trading_strategy
   ```

2. **Create `Procfile`** (for Railway):
   ```
   worker: python3 run_signals_continuous.py
   ```

3. **Create `requirements.txt`** (if not exists):
   ```
   requests>=2.31.0
   pandas>=2.0.0
   numpy>=1.24.0
   pytz>=2023.3
   ```

4. **Deploy to Railway:**
   - Sign up at railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository
   - Railway will auto-detect and deploy

5. **Set Environment Variables:**
   - In Railway dashboard, go to "Variables"
   - Add:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`
     - `CURRENT_CAPITAL`

6. **Done!** Your strategy will run 24/7

---

## 🐧 **Alternative: Oracle Cloud (Most Free)**

If you want the most generous free tier:

### Setup Oracle Cloud VM:

1. **Create VM:**
   - Sign up at oracle.com/cloud
   - Create "Compute Instance" (Always Free)
   - Choose Ubuntu 22.04
   - Get your public IP

2. **SSH and Setup:**
   ```bash
   ssh ubuntu@YOUR_IP
   
   # Install Python and dependencies
   sudo apt update
   sudo apt install python3 python3-pip git -y
   pip3 install requests pandas numpy pytz
   
   # Clone your repo
   git clone YOUR_GITHUB_REPO_URL
   cd final_trading_strategy
   
   # Set environment variables
   export TELEGRAM_BOT_TOKEN='your_token'
   export TELEGRAM_CHAT_ID='your_chat_id'
   export CURRENT_CAPITAL='1000.0'
   ```

3. **Create Systemd Service:**
   ```bash
   sudo nano /etc/systemd/system/trading-strategy.service
   ```
   
   Content:
   ```ini
   [Unit]
   Description=Trading Strategy Service
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/final_trading_strategy
   Environment="TELEGRAM_BOT_TOKEN=your_token"
   Environment="TELEGRAM_CHAT_ID=your_chat_id"
   Environment="CURRENT_CAPITAL=1000.0"
   ExecStart=/usr/bin/python3 /home/ubuntu/final_trading_strategy/run_signals_continuous.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```
   
4. **Start Service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable trading-strategy
   sudo systemctl start trading-strategy
   sudo systemctl status trading-strategy
   ```

---

## 🔄 **Alternative: Render with Cron Jobs**

If using Render, use scheduled tasks instead of continuous running:

1. **Create a "Cron Job" on Render:**
   - Schedule: `0 */4 * * *` (every 4 hours)
   - Command: `cd /opt/render/project/src && python3 mexc_enhanced_strategy.py`

2. **This runs the script every 4 hours** (no need for continuous runner)

---

## 📝 **Files Needed for Cloud Deployment**

### 1. `Procfile` (for Railway/Render):
```
worker: python3 run_signals_continuous.py
```

### 2. `requirements.txt`:
```
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
pytz>=2023.3
```

### 3. `.env.example` (already exists):
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
CURRENT_CAPITAL=1000.0
```

---

## ⚠️ **Important Notes**

1. **Environment Variables**: Never commit secrets to GitHub
2. **Logs**: Check cloud service logs if something goes wrong
3. **Monitoring**: Set up alerts if the service goes down
4. **Costs**: Monitor usage to avoid unexpected charges (though free tiers should be fine)

---

## 🎯 **My Recommendation**

**Start with Railway** - it's the easiest and most reliable:
- ✅ Simple setup
- ✅ No sleeping issues
- ✅ Free tier is generous
- ✅ Easy GitHub integration
- ✅ Good documentation

**Or use Oracle Cloud** if you want:
- ✅ Completely free forever
- ✅ Full control (real VM)
- ✅ More resources

---

*Choose the option that fits your needs best!*


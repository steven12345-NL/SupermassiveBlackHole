# 🚀 Hetzner Cloud Setup Guide for Triton73

**Complete step-by-step guide to deploy Triton73 on Hetzner Cloud**

---

## 📋 Prerequisites

- Hetzner Cloud account (sign up at https://www.hetzner.com/cloud)
- Credit card or PayPal (for verification, but you'll only pay for what you use)
- SSH client (built into macOS/Linux, or PuTTY for Windows)
- Basic terminal knowledge

---

## 🎯 Step 1: Create Hetzner Cloud Account

1. Go to https://www.hetzner.com/cloud
2. Click "Sign Up" or "Register"
3. Fill in your details
4. Verify your email
5. Add payment method (required for verification, but won't be charged until you create resources)

---

## 🖥️ Step 2: Create Your VPS Instance

### 2.1 Create New Project

1. Log into Hetzner Cloud Console
2. Click "New Project"
3. Name it: `Triton73 Trading Bot`
4. Click "Create Project"

### 2.2 Create Server

1. Click "Add Server" or "Create Server"
2. **Choose Location**: 
   - **Recommended**: `Falkenstein` (Germany) or `Nuremberg` (Germany)
   - Both have excellent connectivity to MEXC API
3. **Choose Image**: 
   - Select **Ubuntu 22.04** (LTS - Long Term Support)
4. **Choose Type**:
   - Select **CX11** (€3.29/month)
     - 1 vCPU
     - 2GB RAM
     - 20GB SSD
     - Perfect for your bot
5. **SSH Keys** (Recommended):
   - Click "Add SSH Key"
   - Generate SSH key on your local machine (if you don't have one):
     ```bash
     ssh-keygen -t ed25519 -C "your_email@example.com"
     # Press Enter to accept default location
     # Press Enter for no passphrase (or set one)
     ```
   - Copy your public key:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
   - Paste it into Hetzner Cloud
6. **Name Your Server**: `triton73-bot`
7. Click **"Create & Buy Now"**

**Cost**: €3.29/month (~$3.50/month)

---

## 🔐 Step 3: Connect to Your Server

### 3.1 Get Your Server IP

1. In Hetzner Cloud Console, find your server
2. Copy the **IPv4 address** (e.g., `123.45.67.89`)

### 3.2 SSH into Server

**On macOS/Linux:**
```bash
ssh root@YOUR_SERVER_IP
# Replace YOUR_SERVER_IP with your actual IP
```

**On Windows (using PuTTY):**
- Host: `YOUR_SERVER_IP`
- Port: `22`
- Connection type: `SSH`
- Click "Open"

**First connection**: You'll see a warning about authenticity. Type `yes` to continue.

---

## 🛠️ Step 4: Initial Server Setup

### 4.1 Update System

```bash
# Update package list
apt update

# Upgrade all packages
apt upgrade -y

# Install essential tools
apt install -y curl wget git nano htop
```

### 4.2 Create Non-Root User (Security Best Practice)

```bash
# Create new user
adduser triton73
# Set a strong password when prompted
# Fill in details (or press Enter to skip)

# Add user to sudo group
usermod -aG sudo triton73

# Switch to new user
su - triton73
```

### 4.3 Set Up SSH Key for New User (Optional but Recommended)

```bash
# Create .ssh directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Copy your public key (from your local machine)
# On your LOCAL machine, run:
# cat ~/.ssh/id_ed25519.pub
# Copy the output

# On SERVER, create authorized_keys file
nano ~/.ssh/authorized_keys
# Paste your public key
# Press Ctrl+X, then Y, then Enter to save

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
```

---

## 🐍 Step 5: Install Python and Dependencies

```bash
# Install Python 3.10+ and pip
apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
# Should show: Python 3.10.x or higher

pip3 --version
```

### 5.1 Install Required Python Packages

```bash
# Install system dependencies
apt install -y build-essential python3-dev

# Install Python packages
pip3 install requests pandas numpy pytz
```

---

## 📥 Step 6: Clone Your Repository

### 6.1 Clone from GitHub

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/steven12345-NL/SupermassiveBlackHole.git

# Navigate to strategy directory
cd SupermassiveBlackHole/final_trading_strategy

# Verify files are there
ls -la
```

### 6.2 Make Scripts Executable

```bash
chmod +x *.py *.sh
```

---

## ⚙️ Step 7: Configure Environment Variables

### 7.1 Set Up Telegram Credentials

```bash
# Create environment file
nano ~/.triton73_env
```

Add the following (replace with your actual values):
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
export TELEGRAM_CHAT_ID='your_chat_id_here'
export CURRENT_CAPITAL='1000.0'
export PAPER_CAPITAL='1000.0'
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### 7.2 Load Environment Variables

```bash
# Load environment variables
source ~/.triton73_env

# Verify they're set
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

### 7.3 Make Environment Variables Persistent

Add to your shell profile:
```bash
# Add to .bashrc
echo "source ~/.triton73_env" >> ~/.bashrc

# Reload
source ~/.bashrc
```

---

## 🧪 Step 8: Test Your Setup

### 8.1 Test Telegram Connection

```bash
cd ~/SupermassiveBlackHole/final_trading_strategy
python3 test_telegram.py
```

You should receive a test message on Telegram.

### 8.2 Test Strategy Script (Single Run)

```bash
# Test paper trading (single run)
python3 Triton73_paper_trading.py
```

This should:
- Fetch data from MEXC
- Check for signals
- Display strategy status

---

## 🔄 Step 9: Set Up as System Service (Recommended)

This ensures your bot runs 24/7 and restarts automatically if it crashes.

### 9.1 Create Systemd Service File

```bash
sudo nano /etc/systemd/system/triton73.service
```

Paste the following (adjust paths if needed):
```ini
[Unit]
Description=Triton73 Trading Strategy
After=network.target

[Service]
Type=simple
User=triton73
WorkingDirectory=/home/triton73/SupermassiveBlackHole/final_trading_strategy
EnvironmentFile=/home/triton73/.triton73_env
ExecStart=/usr/bin/python3 /home/triton73/SupermassiveBlackHole/final_trading_strategy/run_paper_trading_continuous.py
Restart=always
RestartSec=10
StandardOutput=append:/home/triton73/triton73.log
StandardError=append:/home/triton73/triton73_error.log

[Install]
WantedBy=multi-user.target
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### 9.2 Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (starts on boot)
sudo systemctl enable triton73

# Start service
sudo systemctl start triton73

# Check status
sudo systemctl status triton73
```

You should see:
```
● triton73.service - Triton73 Trading Strategy
     Loaded: loaded (/etc/systemd/system/triton73.service; enabled)
     Active: active (running) since ...
```

### 9.3 Useful Service Commands

```bash
# Check status
sudo systemctl status triton73

# View logs
sudo journalctl -u triton73 -f

# Stop service
sudo systemctl stop triton73

# Restart service
sudo systemctl restart triton73

# Disable auto-start
sudo systemctl disable triton73
```

---

## 📊 Step 10: Monitor Your Bot

### 10.1 View Logs

```bash
# Real-time logs
tail -f ~/triton73.log

# Or use journalctl
sudo journalctl -u triton73 -f
```

### 10.2 Check Paper Trading Status

```bash
cd ~/SupermassiveBlackHole/final_trading_strategy
python3 check_paper_status.py
```

### 10.3 Generate Health Report

```bash
python3 health_report.py
cat health_report.txt
```

---

## 🔒 Step 11: Security Hardening (Important!)

### 11.1 Set Up Firewall

```bash
# Install UFW (Uncomplicated Firewall)
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 11.2 Disable Root Login (Optional but Recommended)

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Find and change:
# PermitRootLogin yes
# To:
# PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd
```

### 11.3 Set Up Automatic Updates

```bash
# Install unattended-upgrades
sudo apt install -y unattended-upgrades

# Configure
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" when prompted
```

---

## 📈 Step 12: Set Up Monitoring (Optional but Recommended)

### 12.1 Create Monitoring Script

```bash
cd ~/SupermassiveBlackHole/final_trading_strategy
nano monitor_bot.sh
```

Paste:
```bash
#!/bin/bash
# Simple monitoring script

if ! systemctl is-active --quiet triton73; then
    echo "⚠️ Triton73 service is DOWN!"
    # Send Telegram alert (you can add this)
    systemctl restart triton73
fi
```

Make executable:
```bash
chmod +x monitor_bot.sh
```

### 12.2 Set Up Cron Job for Monitoring

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * /home/triton73/SupermassiveBlackHole/final_trading_strategy/monitor_bot.sh >> /home/triton73/monitor.log 2>&1
```

---

## ✅ Step 13: Verify Everything Works

### 13.1 Check Service Status

```bash
sudo systemctl status triton73
```

Should show: `Active: active (running)`

### 13.2 Check Logs

```bash
tail -20 ~/triton73.log
```

Should show recent activity.

### 13.3 Wait for First Signal Check

The bot checks every 4 hours at:
- 00:05 UTC
- 04:05 UTC
- 08:05 UTC
- 12:05 UTC
- 16:05 UTC
- 20:05 UTC

Wait for the next check time and verify you receive Telegram notifications.

---

## 🎯 Quick Reference Commands

```bash
# Service management
sudo systemctl status triton73    # Check status
sudo systemctl restart triton73   # Restart
sudo systemctl stop triton73      # Stop
sudo systemctl start triton73     # Start

# View logs
tail -f ~/triton73.log            # Real-time logs
sudo journalctl -u triton73 -f   # System logs

# Check status
cd ~/SupermassiveBlackHole/final_trading_strategy
python3 check_paper_status.py     # Paper trading status
python3 health_report.py          # Health report

# Update code
cd ~/SupermassiveBlackHole
git pull                          # Pull latest changes
sudo systemctl restart triton73   # Restart service
```

---

## 💰 Cost Breakdown

- **Hetzner Cloud CX11**: €3.29/month (~$3.50/month)
- **Total Annual Cost**: ~€39.48 (~$42/year)

**Very affordable for 24/7 trading bot!**

---

## 🆘 Troubleshooting

### Bot Not Running

```bash
# Check service status
sudo systemctl status triton73

# Check logs
sudo journalctl -u triton73 -n 50

# Restart service
sudo systemctl restart triton73
```

### No Telegram Messages

```bash
# Test Telegram
cd ~/SupermassiveBlackHole/final_trading_strategy
python3 test_telegram.py

# Check environment variables
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

### Can't Connect via SSH

1. Check Hetzner Cloud Console → Firewall settings
2. Verify your IP is allowed
3. Check if server is running in console

### Service Keeps Restarting

```bash
# Check error logs
cat ~/triton73_error.log

# Check system logs
sudo journalctl -u triton73 -n 100
```

---

## 📞 Support Resources

- **Hetzner Cloud Docs**: https://docs.hetzner.com/
- **Hetzner Status**: https://status.hetzner.com/
- **Hetzner Support**: Available in Cloud Console

---

## 🎉 You're All Set!

Your Triton73 strategy is now running 24/7 on Hetzner Cloud!

**Next Steps:**
1. Monitor for first 24-48 hours
2. Check Telegram notifications
3. Review health reports daily
4. Monitor paper trading performance

**Remember:**
- Start with paper trading
- Monitor closely
- Adjust capital as needed
- Review logs regularly

---

**Last Updated**: December 2024  
**Provider**: Hetzner Cloud  
**Plan**: CX11 (€3.29/month)  
**Strategy**: Triton73


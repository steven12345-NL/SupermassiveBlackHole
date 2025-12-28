# 🖥️ VPS Recommendations for Triton73 Strategy

**Best VPS providers for running your trading bot 24/7**

---

## 📊 Requirements Analysis

Your Triton73 strategy needs:
- **CPU**: Minimal (Python script, runs every 4 hours)
- **RAM**: 512MB - 1GB sufficient
- **Storage**: 5-10GB (logs, state files, backups)
- **Network**: Reliable connection for MEXC API calls
- **Uptime**: 99.9%+ (critical for continuous trading)
- **Cost**: As low as possible (long-term running)

---

## 🏆 Top Recommendations

### 1. **Oracle Cloud Free Tier** ⭐ BEST FREE OPTION

**Why it's perfect:**
- ✅ **100% FREE forever** (not a trial)
- ✅ 2 AMD VMs with 1GB RAM each
- ✅ 200GB storage
- ✅ 10TB outbound data transfer
- ✅ 99.95% uptime SLA
- ✅ No credit card required (in some regions)

**Specs:**
- 2x AMD Compute (1/8 OCPU, 1GB RAM)
- 200GB block storage
- 10TB egress/month

**Setup:**
```bash
# Create Ubuntu 22.04 instance
# Install Python 3.9+
sudo apt update
sudo apt install python3 python3-pip git
pip3 install requests pandas numpy
```

**Cost**: **$0/month** (forever free tier)

**Best for**: Long-term free hosting, testing, low-budget deployment

---

### 2. **DigitalOcean** ⭐ BEST PAID OPTION

**Why it's great:**
- ✅ Simple, reliable, well-documented
- ✅ Excellent uptime (99.99%)
- ✅ Fast SSD storage
- ✅ Great community support
- ✅ Easy backups ($1/month)

**Recommended Plan:**
- **Basic Droplet**: $4/month
  - 1 vCPU, 512MB RAM, 10GB SSD
  - 1TB transfer
  - Perfect for your bot

**Cost**: **$4/month** (~$48/year)

**Best for**: Production deployment, reliability, ease of use

---

### 3. **Hetzner Cloud** ⭐ BEST VALUE

**Why it's excellent:**
- ✅ **Best price/performance** in Europe
- ✅ Very fast NVMe SSDs
- ✅ Excellent network (low latency)
- ✅ Simple pricing (no hidden fees)
- ✅ German company (GDPR compliant)

**Recommended Plan:**
- **CX11**: €3.29/month (~$3.50/month)
  - 1 vCPU, 2GB RAM, 20GB SSD
  - 20TB transfer
  - More RAM than DigitalOcean for less money

**Cost**: **€3.29/month** (~$42/year)

**Best for**: European users, best value, high performance

---

### 4. **Vultr** ⭐ BEST GLOBAL COVERAGE

**Why it's good:**
- ✅ 25+ locations worldwide
- ✅ Hourly billing (test before committing)
- ✅ Simple interface
- ✅ Good performance

**Recommended Plan:**
- **Regular Performance**: $2.50/month
  - 1 vCPU, 512MB RAM, 10GB SSD
  - 0.5TB transfer

**Cost**: **$2.50/month** (~$30/year)

**Best for**: Global deployment, testing, flexibility

---

### 5. **Linode (Akamai)** ⭐ BEST SUPPORT

**Why it's reliable:**
- ✅ Excellent customer support
- ✅ 99.99% uptime SLA
- ✅ Good documentation
- ✅ Reliable infrastructure

**Recommended Plan:**
- **Nanode 1GB**: $5/month
  - 1 vCPU, 1GB RAM, 25GB SSD
  - 1TB transfer

**Cost**: **$5/month** (~$60/year)

**Best for**: Support priority, enterprise needs

---

### 6. **AWS Lightsail** ⭐ BEST FOR AWS USERS

**Why it's convenient:**
- ✅ Part of AWS ecosystem
- ✅ Simple pricing
- ✅ Easy integration with other AWS services
- ✅ Good documentation

**Recommended Plan:**
- **Nano**: $3.50/month
  - 1 vCPU, 512MB RAM, 20GB SSD
  - 1TB transfer

**Cost**: **$3.50/month** (~$42/year)

**Best for**: AWS ecosystem users, cloud integration

---

## 🎯 My Top 3 Picks

### For **FREE** (Long-term):
1. **Oracle Cloud Free Tier** - $0/month forever
   - Best if you want zero cost
   - 2 VMs, plenty of resources
   - Reliable (Oracle infrastructure)

### For **BEST VALUE** (Paid):
1. **Hetzner Cloud** - €3.29/month
   - Best price/performance
   - More RAM than competitors
   - Excellent for European users

### For **SIMPLICITY** (Paid):
1. **DigitalOcean** - $4/month
   - Easiest to use
   - Best documentation
   - Great community

---

## 📋 Setup Checklist

Once you choose a VPS:

### 1. **Create Instance**
- Choose Ubuntu 22.04 LTS (most compatible)
- Select smallest plan (sufficient for bot)
- Choose region closest to MEXC servers (Asia-Pacific recommended)

### 2. **Initial Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip git -y

# Install Python packages
pip3 install requests pandas numpy pytz

# Clone your repository (or upload files)
git clone https://github.com/steven12345-NL/SupermassiveBlackHole.git
cd SupermassiveBlackHole/final_trading_strategy
```

### 3. **Configure Environment**
```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN='your_token'
export TELEGRAM_CHAT_ID='your_chat_id'
export CURRENT_CAPITAL=1000.0

# Make scripts executable
chmod +x *.py *.sh
```

### 4. **Run with Screen/Tmux** (Keep running after disconnect)
```bash
# Install screen
sudo apt install screen -y

# Start screen session
screen -S triton73

# Run your strategy
python3 run_paper_trading_continuous.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r triton73
```

### 5. **Or Use systemd Service** (Recommended for production)
Create `/etc/systemd/system/triton73.service`:
```ini
[Unit]
Description=Triton73 Trading Strategy
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/SupermassiveBlackHole/final_trading_strategy
Environment="TELEGRAM_BOT_TOKEN=your_token"
Environment="TELEGRAM_CHAT_ID=your_chat_id"
Environment="CURRENT_CAPITAL=1000.0"
ExecStart=/usr/bin/python3 /home/your_username/SupermassiveBlackHole/final_trading_strategy/run_paper_trading_continuous.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable triton73
sudo systemctl start triton73
sudo systemctl status triton73
```

---

## 🔒 Security Best Practices

1. **SSH Key Authentication** (disable password login)
2. **Firewall Setup** (UFW)
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```
3. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
4. **Monitor Logs**
   ```bash
   tail -f paper_trading.log
   ```

---

## 💰 Cost Comparison

| Provider | Monthly | Yearly | Best For |
|----------|---------|--------|----------|
| **Oracle Cloud** | $0 | $0 | Free tier, long-term |
| **Vultr** | $2.50 | $30 | Budget, global |
| **Hetzner** | €3.29 | €39 | Value, Europe |
| **AWS Lightsail** | $3.50 | $42 | AWS ecosystem |
| **DigitalOcean** | $4.00 | $48 | Simplicity, reliability |
| **Linode** | $5.00 | $60 | Support, enterprise |

---

## 🎯 Final Recommendation

**For most users**: Start with **Oracle Cloud Free Tier** (free forever)
- Test your strategy for free
- No commitment
- Upgrade later if needed

**If you need paid**: Choose **Hetzner Cloud** (best value) ⭐ RECOMMENDED
- €3.29/month
- More resources than competitors
- Excellent performance
- **See `HETZNER_SETUP_GUIDE.md` for complete step-by-step setup**

**If simplicity matters**: Choose **DigitalOcean** ($4/month)
- Easiest to use
- Best documentation
- Great community support

---

## 📞 Quick Links

- **Oracle Cloud**: https://www.oracle.com/cloud/free/
- **Hetzner Cloud**: https://www.hetzner.com/cloud
- **DigitalOcean**: https://www.digitalocean.com/
- **Vultr**: https://www.vultr.com/
- **AWS Lightsail**: https://aws.amazon.com/lightsail/
- **Linode**: https://www.linode.com/

---

## ⚠️ Important Notes

1. **Always start with paper trading** on VPS before live trading
2. **Monitor for first 24-48 hours** to ensure stability
3. **Set up automated backups** of state files
4. **Use monitoring** (health_report.py daily)
5. **Keep logs** for troubleshooting

---

**Last Updated**: December 2024  
**Strategy**: Triton73  
**Recommended**: Oracle Cloud (free) or Hetzner Cloud (paid)


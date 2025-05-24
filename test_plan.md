# OSCE Testing Checklist

## Before Going Live

### 1. Test on Fresh Raspberry Pi

- [ ] Flash fresh Raspberry Pi OS
- [ ] Connect to WiFi
- [ ] Run installer:
  ```bash
  curl -sSL https://raw.githubusercontent.com/HydroFarmerJason/OpenSourceControlledEnvironments/main/install.sh | bash
  ```
- [ ] Verify no errors during install
- [ ] Dashboard loads at http://pi-ip:8080
- [ ] Shows "No sensors detected" message

### 2. Test Sensor Detection

#### With DHT22:
- [ ] Connect DHT22 to pin 4 (with resistor)
- [ ] Restart OSCE or wait 30 seconds
- [ ] Temperature appears on dashboard
- [ ] Values update every 2 seconds

#### Without Sensors:
- [ ] Mock sensor appears after 30 seconds
- [ ] Shows demo temperature that changes

### 3. Test Different Platforms

#### Raspberry Pi 4:
- [ ] Installer detects "Raspberry Pi 4"
- [ ] I2C warning appears if not enabled
- [ ] Completes in under 2 minutes

#### Raspberry Pi Zero W:
- [ ] Installer detects "Raspberry Pi Zero"
- [ ] Works on limited RAM
- [ ] Dashboard still responsive

#### Ubuntu/Debian VM:
- [ ] Installer detects "Generic Linux"
- [ ] Mock sensors work
- [ ] No GPIO errors

### 4. Test Error Conditions

- [ ] No internet after install starts
- [ ] Python 3.6 (should fail gracefully)
- [ ] Disk full (should show clear error)
- [ ] Already installed (should detect)

### 5. Test with First Educator

**Send them this message:**

```
Hi [Name],

Ready to test our new greenhouse monitoring system? 

Just paste this command on your Raspberry Pi:

curl -sSL https://raw.githubusercontent.com/HydroFarmerJason/OpenSourceControlledEnvironments/main/install.sh | bash

Let me know:
1. Did it work first try?
2. Could you see the dashboard?
3. What confused you?
4. What would make it better?

No coding needed - just run that one command!

Thanks!
```

**Track their feedback:**
- [ ] Installation time: ______
- [ ] Confusion points: ______
- [ ] Suggestions: ______
- [ ] Would they recommend it? ______

### 6. Performance Tests

- [ ] Dashboard loads in < 2 seconds
- [ ] Uses < 100MB RAM
- [ ] CPU usage < 5% when idle
- [ ] Survives 24 hours running

### 7. Security Quick Check

- [ ] Only listens on port 8080
- [ ] No default passwords
- [ ] No sudo required after install
- [ ] Runs as user, not root

## Launch Readiness Checklist

### Documentation
- [ ] README.md has working install command
- [ ] License file exists
- [ ] Basic troubleshooting in README

### Code
- [ ] installer.sh in main branch
- [ ] No hardcoded IPs or passwords
- [ ] Error messages are helpful

### Community
- [ ] GitHub Issues enabled
- [ ] Discussions enabled
- [ ] Welcome message ready

## First Day Launch Plan

### Hour 1
- Upload installer.sh
- Test one-line install yourself
- Fix any immediate issues

### Hour 2
- Send to PhD consultant
- Watch them install remotely
- Note confusion points

### Hour 3
- Fix issues found
- Update documentation
- Test again

### Hour 4
- Share with 2-3 friendly testers
- Create demo GIF/video
- Prepare social media post

### Day 2
- Fix feedback from testers
- Polish documentation
- Share publicly

## Success Metrics

### Day 1
- [ ] 5 successful installs
- [ ] 0 "doesn't work" reports
- [ ] 1 piece of positive feedback

### Week 1
- [ ] 20 installs
- [ ] 10 GitHub stars
- [ ] 1 community plugin idea

### Month 1
- [ ] 100 installs
- [ ] 50 GitHub stars
- [ ] 3 contributors

## Common Issues & Fixes

### "Command not found: curl"
```bash
sudo apt-get update && sudo apt-get install -y curl
```

### "Permission denied"
```bash
# Don't run as root, run as pi user
```

### "Port 8080 already in use"
```bash
# Check what's using it
sudo lsof -i :8080
# Change port in core.py if needed
```

### "No sensors detected"
Normal! This means:
- No DHT22 on pin 4
- No 1-Wire sensors
- Mock sensor will appear soon

## Emergency Fixes

If something is broken and people are trying to install:

### Option 1: Quick Fix
1. Fix the issue in install.sh
2. Commit immediately
3. Tell users to retry

### Option 2: Rollback
```bash
git revert HEAD
git push
```

### Option 3: Add Notice
Add to top of README:
```markdown
 **Known Issue**: [Description]. Fix coming soon! For now, [workaround].
```

---

## Remember the Goal

 Someone runs ONE command
 They see a dashboard in their browser
 Their sensors appear automatically
 They think "Wow, that was easy!"

Everything else can wait for v1.1

**The dream**: Your first test educator texts you: "Holy crap, it just worked!"

Ready? Let's do this! 

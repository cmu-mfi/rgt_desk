# rgt_desk
Absolutely life-changing dashboard experience unlike anything you have ever seen before. Truly eye-opening. Let's grind!

# Dependencies
Make sure you have a recent version of nodejs installed. I would recommend using nvm like this:
```bash
nvm install 24
```

# Install

1. Clone this repo:
```bash
git clone https://github.com/alexmnr/rgt_desk.git
```

2. Run the install script:
```bash
cd rgt_desk && ./install.sh
```

3. Check the status of the frontend and backend:
```bash
sudo systemctl status rgt_desk_backend.service
sudo systemctl status rgt_desk_frontend.service
```

# Restart
After for changes in the code base to be reflected on the dashboard run these commands:
```bash
sudo systemctl restart rgt_desk_backend.service
sudo systemctl restart rgt_desk_frontend.service
```

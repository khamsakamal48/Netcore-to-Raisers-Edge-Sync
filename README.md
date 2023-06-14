# Netcore-to-Raisers-Edge-Sync

### Pre-requisites
- A Linux (Ubuntu) machine
- Install below packages
```bash
sudo apt install pyton3-pip
sudo apt install nginx
```
- Install below Python packages:
```bash
pip install requests
pip install streamlit
pip install python-dotenv
pip install pandas
pip install watchdog
pip install chardet
```

### Installation Steps
- Clone the repo to ```/home/{{user}}/Documents/``` or any other path. Make sure to change the path in below code snippets as well.
- Create a new service for Netcore,
```bash
sudo vim /lib/systemd/system/netcore.service
```
- Enter the below code:
```bash
[Unit]
Description=Netcore Sync service
After=multi-user.target

[Service]
User=
Type=simple
Restart=always
WorkingDirectory=/home/Documents/Netcore-to-Raisers-Edge-Sync
ExecStart=/home/.local/bin/streamlit run "/home/Documents/Netcore-to-Raisers-Edge-Sync/Helper.py"

[Install]
WantedBy=multi-user.target
```
- Start the service
```bash
sudo systemctl start netcore.service
```


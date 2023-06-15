# Netcore to Raisers Edge Sync

## Pre-requisites
- A Linux (Ubuntu) machine
- Install below packages
```bash
sudo apt install python3-pip
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

## Installation Steps
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
- Create a new nginx configuration file or make changes (if exists already)
```bash
sudo vim /etc/nginx/sites-available/streamlitnginxconf
```
- Paste the below content in the file:
```bash
server {
    listen 80;
    server_name 10.199.4.149;
    client_max_body_size 200M;

    location /netcore {
        proxy_pass http://127.0.0.1:8502/netcore;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
- Enable the file by linking it to sites-enabled directory
```bash
sudo ln -s /etc/nginx/sites-available/streamlitnginxconf /etc/nginx/sites-enabled
```
- Test Nginx configuration for syntax errors by typing:
```bash
sudo nginx -t
```
- If no errors are reported, go ahead and restart Nginx:
```bash
sudo systemctl restart nginx
```


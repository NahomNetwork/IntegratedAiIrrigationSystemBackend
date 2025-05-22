## Deploying to a VPS

To deploy the backend system to a VPS, follow these steps:

---

### 1. Update and Install Required Packages

Ensure your VPS is up-to-date and install the necessary packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install nginx certbot python3-certbot-nginx docker.io docker-compose -y
```

---

### 2. Set Up Docker (Optional)

If you plan to use Docker for deployment:

1. **Enable Docker Service**:

   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Build and Run the Docker Image**:

   ```bash
   docker build -t backend-system .
   docker run -d -p 8000:8000 --env-file .env backend-system
   ```

---

### 3. Configure Nginx

1. **Create a New Nginx Configuration File**:

   ```bash
   sudo nano /etc/nginx/sites-available/myapp
   ```

2. **Add the Following Configuration**:

   Replace `<your_domain>` with your domain name and `<your_server_ip>` with your VPS IP address.

   ```nginx
   server {
       listen 80;
       server_name <your_domain>;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /path/to/static/files/;
       }
   }
   ```

3. **Enable the Configuration**:

   ```bash
   sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

### 4. Set Up HTTPS with Certbot

1. **Obtain an SSL Certificate**:

   Ensure your domain is pointing to your VPS IP address (via DNS settings).

   ```bash
   sudo certbot --nginx -d <your_domain>
   ```

2. **Verify HTTPS Setup**:

   Visit `https://<your_domain>` in your browser to confirm the SSL certificate is working.

3. **Automate Certificate Renewal**:

   Certbot automatically sets up a cron job for renewal. You can manually test it with:

   ```bash
   sudo certbot renew --dry-run
   ```

---

### 5. Run the Application

If not using Docker, follow these steps:

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run Database Migrations**:

   ```bash
   alembic upgrade head
   ```

3. **Start the Application**:

   Use a process manager like `gunicorn` or `uvicorn` with `systemd` for production:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

### 6. Configure Systemd for Application (Optional)

To ensure the application runs as a service:

1. **Create a Systemd Service File**:

   ```bash
   sudo nano /etc/systemd/system/backend.service
   ```

2. **Add the Following Configuration**:

   ```ini
   [Unit]
   Description=Backend System
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/your/project
   ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start the Service**:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable backend.service
   sudo systemctl start backend.service
   ```

4. **Check Service Status**:

   ```bash
   sudo systemctl status backend.service
   ```

---

### 7. Monitor Logs

To monitor application logs, use:

```bash
journalctl -u backend.service -f
```

---

### 8. Firewall Configuration (Optional)

If using `ufw` (Uncomplicated Firewall), allow necessary ports:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

### Notes

- Ensure your `.env` file is properly configured with database credentials and other environment variables.
- Regularly update your system and dependencies to ensure security and stability.

---

With these steps, your backend system should be successfully deployed and accessible via your domain.

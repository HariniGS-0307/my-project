# AI Elderly Medicare System Deployment Guide

## Deployment Options

The AI Elderly Medicare System can be deployed in several ways:

1. **Docker Compose** (Recommended for small to medium deployments)
2. **Kubernetes** (Recommended for large scale deployments)
3. **Traditional Server Deployment** (Manual setup)

## Docker Compose Deployment

### Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 1.29 or higher

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/ai-elderly-medicare-system.git
   cd ai-elderly-medicare-system
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Run database migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Seed initial data:
   ```bash
   docker-compose exec web python manage.py seed_data
   ```

### Scaling

To scale the web application:
```bash
docker-compose up -d --scale web=3
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (v1.20 or higher)
- kubectl CLI
- Helm 3 (optional)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/ai-elderly-medicare-system.git
   cd ai-elderly-medicare-system
   ```

2. Create namespace:
   ```bash
   kubectl create namespace medicare-system
   ```

3. Deploy the application:
   ```bash
   kubectl apply -f deployment/kubernetes/ -n medicare-system
   ```

4. Configure secrets:
   ```bash
   kubectl create secret generic app-secrets \
     --from-env-file=.env \
     -n medicare-system
   ```

5. Verify deployment:
   ```bash
   kubectl get pods -n medicare-system
   ```

### Ingress Configuration

The system includes an ingress configuration for external access. Update the domain in `deployment/kubernetes/ingress.yaml` to match your domain.

## Traditional Server Deployment

### Prerequisites

- Ubuntu 20.04 or CentOS 8
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Nginx
- Systemd

### Steps

1. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip postgresql redis nginx
   ```

2. Create application user:
   ```bash
   sudo useradd -r -s /bin/false medicare
   ```

3. Clone repository:
   ```bash
   sudo mkdir -p /opt/medicare-system
   sudo chown medicare:medicare /opt/medicare-system
   git clone https://github.com/your-organization/ai-elderly-medicare-system.git /opt/medicare-system
   ```

4. Install Python dependencies:
   ```bash
   cd /opt/medicare-system
   pip3 install -r requirements.txt
   ```

5. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

6. Set up database:
   ```bash
   sudo -u postgres createdb medicare_db
   python3 manage.py migrate
   python3 manage.py seed_data
   ```

7. Configure systemd service:
   ```bash
   sudo cp deployment/systemd/medicare.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable medicare
   sudo systemctl start medicare
   ```

8. Configure Nginx:
   ```bash
   sudo cp deployment/nginx/medicare.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/medicare.conf /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## SSL Configuration

For production deployments, SSL certificates should be configured:

### Let's Encrypt with Certbot

1. Install Certbot:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. Obtain certificate:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## Monitoring and Logging

### Health Checks

The application provides health check endpoints:

- `/health/` - Basic health check
- `/health/database/` - Database connectivity check
- `/health/redis/` - Redis connectivity check

### Log Management

Logs are written to:
- `/var/log/medicare/` (traditional deployment)
- Docker logs (Docker deployment)
- Pod logs (Kubernetes deployment)

## Backup and Recovery

### Database Backup

```bash
python3 manage.py backup_database
```

### Restore Database

```bash
python3 manage.py restore_database backup_file.sql
```

## Maintenance

### Updating the Application

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Install new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python3 manage.py migrate
   ```

4. Restart services:
   ```bash
   sudo systemctl restart medicare  # Traditional
   # OR
   docker-compose restart  # Docker
   # OR
   kubectl rollout restart deployment/medicare-app  # Kubernetes
   ```

## Security Considerations

1. Always use HTTPS in production
2. Regularly update dependencies
3. Implement proper firewall rules
4. Use strong passwords and rotate them regularly
5. Enable two-factor authentication for admin accounts
6. Regularly backup data and test recovery procedures
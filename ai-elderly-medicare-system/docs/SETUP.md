# AI Elderly Medicare System Setup Guide

## Prerequisites

Before installing the AI Elderly Medicare System, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis 6 or higher
- Node.js 14 or higher (for frontend development)
- Docker (optional, for containerized deployment)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/ai-elderly-medicare-system.git
cd ai-elderly-medicare-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```
# Database
DATABASE_URL=postgresql://user:password@localhost/medicare_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (for notifications)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-email-password

# Twilio (for SMS notifications)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

### 5. Database Setup

Create the database and run migrations:

```bash
python manage.py create_database
python manage.py migrate
```

### 6. Seed Initial Data

```bash
python manage.py seed_data
```

## Running the Application

### Development Server

```bash
python run_server.py
```

The application will be available at `http://localhost:8000`.

### Production Server

For production deployment, use the Docker configuration:

```bash
docker-compose up -d
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## Frontend Development

To work on the frontend components:

```bash
cd frontend
npm install
npm run dev
```

## Mobile API

The mobile API is available at `http://localhost:8000/api/v1/`.

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Verify database credentials in `.env`

2. **Redis Connection Error**
   - Ensure Redis is running
   - Verify Redis URL in `.env`

3. **Missing Dependencies**
   - Run `pip install -r requirements.txt` again

### Support

For additional support, please contact the development team or refer to the documentation.
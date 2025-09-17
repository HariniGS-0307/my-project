# AI Elderly Medicare System API Documentation

## Overview

This document provides comprehensive documentation for the AI Elderly Medicare System API. The API is built using FastAPI and follows RESTful principles to provide seamless integration with mobile applications and external systems.

## Authentication

All API endpoints require authentication using JWT tokens. Tokens are obtained through the authentication endpoints and must be included in the `Authorization` header of all requests.

```
Authorization: Bearer <token>
```

## API Endpoints

### Authentication

#### POST /api/auth/login
Authenticate a user and obtain an access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "patient"
  }
}
```

#### POST /api/auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "patient"
}
```

### Patients

#### GET /api/patients
Retrieve a list of patients (admin only).

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

#### GET /api/patients/{patient_id}
Retrieve details for a specific patient.

#### PUT /api/patients/{patient_id}
Update patient information.

#### DELETE /api/patients/{patient_id}
Delete a patient record.

### Medications

#### GET /api/medications
Retrieve a list of medications for the authenticated user.

#### POST /api/medications
Add a new medication.

#### GET /api/medications/{medication_id}
Retrieve details for a specific medication.

#### PUT /api/medications/{medication_id}
Update medication information.

#### DELETE /api/medications/{medication_id}
Delete a medication record.

### Appointments

#### GET /api/appointments
Retrieve a list of appointments for the authenticated user.

#### POST /api/appointments
Schedule a new appointment.

#### GET /api/appointments/{appointment_id}
Retrieve details for a specific appointment.

#### PUT /api/appointments/{appointment_id}
Update appointment information.

#### DELETE /api/appointments/{appointment_id}
Cancel an appointment.

### Notifications

#### GET /api/notifications
Retrieve a list of notifications for the authenticated user.

#### POST /api/notifications
Create a new notification.

#### PUT /api/notifications/{notification_id}/read
Mark a notification as read.

### Delivery

#### GET /api/deliveries
Retrieve delivery information for the authenticated user.

#### GET /api/deliveries/{delivery_id}
Retrieve details for a specific delivery.

## Error Responses

All error responses follow a consistent format:

```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

The API implements rate limiting to prevent abuse. Each IP address is limited to 1000 requests per hour.

## WebSockets

The system supports real-time notifications through WebSockets.

### WebSocket Endpoint
```
ws://api.example.com/ws/notifications
```

### Events
- `notification`: New notification received
- `appointment_update`: Appointment status changed
- `medication_reminder`: Medication reminder triggered
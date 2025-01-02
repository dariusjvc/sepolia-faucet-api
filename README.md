# Faucet Application - README

## Overview
This application provides a faucet service that allows users to receive free Sepolia ETH. This service is especially useful for developers who need test Ether to interact with the Sepolia Ethereum test network. The application processes requests asynchronously, ensuring that users can receive small amounts of ETH quickly and efficiently without overloading the server. The application has two main endpoints:

1. **POST /faucet/fund**: Sends 0.0001 Sepolia ETH to a specified wallet address.
2. **GET /faucet/stats**: Returns statistics about successful and failed transactions in the last 24 hours.

## Introduction
The Sepolia test network is a critical environment for Ethereum developers to test their applications without the risks associated with using real Ether. This faucet application simplifies the process of obtaining test ETH, enabling developers to focus on building and testing their projects.

## Requirements

- **Django (>=3.2, <4.0)**: Django is a high-level Python web framework that encourages rapid development and clean design. In this application, Django handles the web server, data management, and the creation of routes or endpoints.

- **djangorestframework (==3.14.0)**: Django REST Framework (DRF) is a toolkit for building Web APIs using Django. It provides features such as data serialization, validation, authentication, and authorization, enabling the creation of secure and efficient APIs.

- **drf-yasg (==1.21.5)**: DRF-YASG is a tool that automatically generates documentation for APIs built with Django REST Framework. It uses the OpenAPI/Swagger format, allowing developers and users to view and interact with the API documentation.

- **web3 (==5.29.1)**: Web3.py is a library that enables interaction with the Ethereum blockchain from Python. In this application, Web3.py is used to execute transactions on the Ethereum network, such as sending Sepolia ETH.

- **psycopg2-binary**: Psycopg2 is the most popular PostgreSQL adapter for Python. This package allows Django to connect and interact with a PostgreSQL database efficiently.

- **celery (==5.4.0)**: Celery is an asynchronous task queue/job queue based on distributed message passing. It is used in this application to handle transaction processes asynchronously, improving scalability and performance.

- **redis (==4.0.0)**: Redis is an in-memory data structure store used as a message broker by Celery. In this application, Redis is responsible for handling the task queue for processing transactions asynchronously.

## .env file
It is crucial to create a `.env` file at the root of the project. This file contains sensitive configuration details required for the application to function correctly. Below is an example of the `.env` file:

- PRIVATE_KEY=YOUR_PRIVATE_KEY
- FAUCET_ADDRESS=YOUR_FAUCET_ADDRESS
- SECRET_KEY=YOUR_SECRET_KEY

**Explanation of Variables**

PRIVATE_KEY:
- This is the private key of an Ethereum wallet that the faucet will use to send Sepolia ETH.
- The wallet must have Sepolia ETH available. You can obtain test ETH from a Sepolia faucet.
- ⚠️ Important: Keep this private key secure and never share it publicly or commit it to a repository.

FAUCET_ADDRESS:
- The public address of the Ethereum wallet associated with the faucet.
- This is the address that will be used to send Sepolia ETH to users requesting funds.

SECRET_KEY:
- This is the Django **`SECRET_KEY`**, which is required for cryptographic operations, such as session management and password hashing.
- Use a securely generated key for production environments to ensure the security of your Django application.

**Security Notes**
- Never commit your `.env` file to the repository. Add it to your `.gitignore` file to prevent accidental exposure.
- Ensure that the Ethereum wallet you use for the faucet has sufficient Sepolia ETH for testing.
- Use tools like Vault or encrypted environment variable management solutions for enhanced security in production environments.


## Setup Instructions

1. **Build and run the application using Docker**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Make database migrations** (if necessary):
   ```bash
   docker-compose run web python manage.py makemigrations myapi
   docker-compose run web python manage.py migrate
   ```
The following services will be started:

- **company-web**: Handles the Django web server, managing the API endpoints and the interaction with the database.
- **company-celery**: Runs the Celery worker responsible for processing fund transactions asynchronously.
- **redis**: Acts as a message broker for Celery, managing the task queue for transaction processing.

## Swagger Documentation

For your convenience, you can access the API documentation via Swagger, which provides an interactive interface for testing the endpoints without the need to use `curl` or other tools. You can easily explore the available endpoints, review their parameters, and send requests directly from the browser.

## Access the Swagger Documentation
🚀 **Explore the API documentation here:**  
[**http://localhost:8000/api/docs/v1/company**](http://localhost:8000/api/docs/v1/company)

## Endpoints

### 1. POST /faucet/fund

#### Description
This endpoint accepts a wallet address as a query parameter and sends 0.0001 Sepolia ETH from a pre-configured wallet to the specified address.

#### Request Example
   ```bash
   curl -X 'POST' \
   'http://localhost:8000/faucet/fund/?wallet_address=<YOUR_WALLET_ADDRESS>' \
   -H 'accept: application/json' \
   -H 'X-CSRFToken: <your_csrf_token>' \
   -d ''
   ```
#### Responses:
##### 200: Funds sent successfully. Returns the transaction ID.:
   ```bash
   {
   "message": "Funds sent!",
   "transaction_id": "0xa301cc0bd2176ff36c0ef3b50ae8a5e7e33a41e6efdea8fcce351eb105c0c352"
   }
   ```
##### 400: Invalid method. Wallet address may be missing or incorrect.:
   ```bash
   {
   "message": "Funds sent!",
   "transaction_id": "0xa301cc0bd2176ff36c0ef3b50ae8a5e7e33a41e6efdea8fcce351eb105c0c352"
   }
   ```
##### 429: Rate limit exceeded. Users can only request funds once per minute.:
   ```bash
   {
   "error": "Rate limit exceeded. Please try again later."
   }
   ```

### 2. GET /faucet/stats

#### Description
This endpoint returns the number of successful and failed transactions in the last 24 hours.

#### Request Example
   ```bash
   curl -X 'GET' \
   'http://localhost:8000/faucet/stats/' \
   -H 'accept: application/json' \
   -H 'X-CSRFToken: <your_csrf_token>'
   ```
#### Responses:
##### 200: Returns the count of successful and failed transactions in the last 24 hours.:
   ```bash
   {
   "successful_transactions": 10,
   "failed_transactions": 2
   }
   ```
##### 400: Invalid method. The request could not be processed.:
   ```bash
   {
   "error": "Invalid method. The request could not be processed."
   }
   ```

## Asynchronous Processing

The application leverages **Celery** to handle fund transactions asynchronously. This means that requests to send Sepolia ETH are placed in a queue and processed in the background, allowing the API to respond quickly without waiting for the transaction to complete.

**Redis** acts as the message broker, managing the queue of tasks and ensuring that transactions are processed in the correct order. This setup improves both scalability and reliability, ensuring that the application can handle multiple requests without overloading the server.

This architecture allows the application to scale horizontally by adding more workers, improving the overall throughput and efficiency.

## Database Setup
The application uses SQLite by default for simplicity. However, if you prefer to use PostgreSQL, you can set it up by following these steps:

1. Update `DATABASES` in `settings.py`:
   ```python
   DATABASES = {
      'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': BASE_DIR / "db.sqlite3",
      }
   }
   ```

2. Run the migrations:

   ```bash
   docker-compose run web python manage.py migrate
   ```

## Local Setup (Without Docker)

If you prefer to run the application locally without Docker, follow these steps:

1. **Create a virtual environment**:
   ```bash
   python -m venv env
   source env/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```
4. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
## Environment Variables

The application requires the following environment variables to be set for proper configuration. These variables are defined in the `docker-compose.yml` file and are used to configure the Django application, Celery, and Redis:

- **DJANGO_SETTINGS_MODULE**: Specifies the settings file to be used for Django. This should point to your Django settings file. In this case, it is set to `myproject.settings`.
  
- **SECRET_KEY**: This is the secret key used by Django for cryptographic signing. Replace the example key with a securely generated one for production environments.
  
- **REDIS_URL**: The URL of the Redis instance used by Celery as the broker for asynchronous task management. In this setup, Redis runs in a Docker container, so the URL is `redis://redis:6379/0`.

- **PRIVATE_KEY**: This is the Ethereum private key used to send Sepolia ETH. Ensure that this key is stored securely and never exposed in production environments.

- **ALLOWED_HOSTS**: A comma-separated list of the host/domain names that Django is allowed to serve. Typically includes `localhost` and `127.0.0.1` for local development.

- **DEBUG**: Determines whether Django runs in debug mode. Set to `True` for development, but it should be `False` in production.

- **CELERY_BROKER_URL**: The broker URL for Celery, which is responsible for managing task queues. In this setup, Celery uses Redis, so the URL is `redis://redis:6379/0`.

- **CELERY_RESULT_BACKEND**: The backend URL for Celery to store the results of the executed tasks. In this case, it's also using Redis.

## Improvements

### Handling Pending Transactions

Currently, the application does not handle transactions that remain in a "pending" state. To improve this, a new feature could be implemented to track these transactions and update their status once finalized. Below is a suggested approach:

1. **Add a New State in the Transaction Model**:
   - Extend the transaction model to include a new status, such as `PENDING`, in addition to the existing statuses (e.g., `SUCCESS`, `FAILED`).

2. **Periodic Status Check**:
   - Implement a periodic task using **Celery** to query the blockchain for the status of transactions that are still marked as `PENDING`.
   - If a transaction is confirmed on the blockchain, update its status to `SUCCESS`. If it fails, mark it as `FAILED`.

3. **Benefits**:
   - Ensures that pending transactions are tracked until they are finalized.
   - Provides users with accurate feedback on the status of their requests.

4. **Implementation Note**:
   - The frequency of the periodic task should be configured to avoid overloading the blockchain or the server. For instance, you can run the task every few minutes.

5. **User Notification**:
   - Optional: Add a feature to notify users when their transaction status changes from `PENDING` to either `SUCCESS` or `FAILED`, through email or other means.

This improvement would enhance the reliability and user experience of the application by ensuring that all transactions are processed and their final statuses are accurately reported.


## Conclusion
This application provides a simple faucet service for Sepolia ETH, demonstrating the use of Django REST Framework with Docker, Celery, and Redis for asynchronous task processing. It is a scalable solution designed to handle requests efficiently while ensuring system stability.
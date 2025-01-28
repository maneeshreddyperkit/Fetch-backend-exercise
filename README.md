# Fetch-backend-exercise

# Receipt Points Calculator

This is a Flask-based web application for calculating points based on receipt details. The application processes receipts submitted via a POST request and calculates points based on specific rules. Users can also retrieve the points for a processed receipt using its unique ID.

## Features

- Calculate points based on various receipt attributes (e.g., retailer name, total amount, item details).
- Unique receipt ID generation.
- REST API endpoints for processing receipts and retrieving points.

---

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.7 or later
- pip (Python package manager)

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate     # For Windows

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py

2. **Access the application**: The server will start on http://127.0.0.1:5000 by default.

## API Endpoints

### 1. Process a Receipt

- Endpoint: /receipts/process

- Method: POST

- Description: Submit a receipt for processing and receive a unique receipt ID.

- Request Example:
```json
{
  "retailer": "Walmart",
  "total": "20.00",
  "items": [
    { "shortDescription": "Milk", "price": "2.50" },
    { "shortDescription": "Bread", "price": "1.50" }
  ],
  "purchaseDate": "2025-01-25",
  "purchaseTime": "15:30"
}
```

- Response example:
```json
{
  "id": "e3b0c442-98fc-1c14-9afb-d4e0fb2a5ec6"
}
```

### 2. Get Points for a Receipt

- Endpoint: /receipts/<receipt_id>/points

- Method: GET

- Description: Retrieve the points for a specific receipt using its unique ID.

- Response Example:
```json
{
  "points": 105
}
```

## Running Tests:

To verify the application works as expected, you can use tools like Postman, curl, or write Python tests with unittest.

# Example using Curl

### 1. Process a receipt:
```bash
   curl -X POST http://127.0.0.1:5000/receipts/process -H "Content-Type: application/json" -d '{
    "retailer": "Walmart",
    "total": "20.00",
    "items": [
        { "shortDescription": "Milk", "price": "2.50" },
        { "shortDescription": "Bread", "price": "1.50" }
    ],
    "purchaseDate": "2025-01-25",
    "purchaseTime": "15:30"
}'
```

### 2. Get Points:

```bash
   curl -X GET http://127.0.0.1:5000/receipts/<receipt_id>/points
```

Replace <receipt_id> with the actual ID returned from the /receipts/process endpoint.

# Receipt Points Calculator (Dockerized Setup)

This guide explains how to run the Receipt Points Calculator using Docker. By containerizing the application, you can ensure a consistent environment without worrying about dependencies or Python versions on your local machine.

---

## Docker Setup

### 1. Create a `Dockerfile`

Add the following `Dockerfile` to the root directory of your project:

```dockerfile
# Use the official Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
```

### 2. Build the Docker image:

Run the following command in the root directory of your project (where the Dockerfile is located):

```bash
   docker build -t receipt-points-calculator .
```

### 3. Run the Docker container:

To run the application in a Docker container, use the following command:
```bash
docker run -p 5000:5000 receipt-points-calculator
```
- -p 5000:5000: Maps port 5000 on the host machine to port 5000 in the container.
- receipt-points-calculator: The name of the Docker image built in the previous step.

### 4. Access the application:

Once the container is running, you can access the application at:
```arduino
http://localhost:5000
```

## Environment Variables
To run this application, you need to set up environment variables in a `.env` file.

Example `.env` file:
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

- `FLASK_ENV`: Set to `development` for debug mode or `production` for live environments.
- `SECRET_KEY`: A secret key used for securely signing sessions in Flask.


## Notes
- The application uses in-memory storage, so all processed receipts will be lost when the server stops.
- Ensure you replace <repository_url> with the actual Git repository URL.

## License

This project is open-source and available under the MIT License.










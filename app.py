# Import necessary libraries
from flask import Flask, request, jsonify  # Flask for web framework, request and jsonify for handling HTTP requests and responses
import uuid  # UUID to generate unique IDs for each receipt
import re  # Regex, though not currently used in this code
from datetime import datetime  # For parsing and comparing date and time
from dotenv import load_dotenv  # Import dotenv for loading environment variables
import os  # Import os module for accessing environment variables

# Load environment variables
load_dotenv()  # Load the environment variables from a .env file

# Initialize the Flask application
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  
# Set the application's secret key using the value from the "SECRET_KEY" environment variable
# If "SECRET_KEY" is not defined in the .env file, it defaults to "default_secret_key"

flask_env = os.getenv("FLASK_ENV", "production")  
# Retrieve the "FLASK_ENV" environment variable to determine the application's environment
# Default to "production" if the variable is not set in the .env file

print(f"Running in {flask_env} mode")  
# Print a message indicating the current environment mode of the application

# In-memory storage for storing processed receipts and their points
receipts_data = {}

# Validation Regex Patterns
RETAILER_REGEX = r"^[\w\s\-\&]+$"  # Retailer name can include alphanumeric characters, spaces, hyphens, and ampersands
TOTAL_REGEX = r"^\d+\.\d{2}$"  # Total must match the pattern of a valid monetary value (e.g., "6.49")
PRICE_REGEX = r"^\d+\.\d{2}$"  # Item price must match the pattern of a valid monetary value (e.g., "6.49")
DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"  # Date must be in the format YYYY-MM-DD
TIME_REGEX = r"^\d{2}:\d{2}$"  # Time must be in the format HH:MM

# Function to validate receipt fields based on the API schema
def validate_receipt(receipt):
    # Validate retailer name
    if not re.match(RETAILER_REGEX, receipt.get("retailer", "")):
        return "Invalid retailer name format", 400

    # Validate total amount
    total = receipt.get("total", "")
    if not re.match(TOTAL_REGEX, total):
        return "Invalid total amount format", 400

    # Validate purchase date
    purchase_date = receipt.get("purchaseDate", "")
    if not re.match(DATE_REGEX, purchase_date):
        return "Invalid purchase date format, expected YYYY-MM-DD", 400

    # Validate purchase time
    purchase_time = receipt.get("purchaseTime", "")
    if not re.match(TIME_REGEX, purchase_time):
        return "Invalid purchase time format, expected HH:MM", 400

    # Validate items list
    items = receipt.get("items", [])
    if not isinstance(items, list) or len(items) < 1:
        return "Items must be a non-empty array", 400

    # Validate each item's short description and price
    for item in items:
        description = item.get("shortDescription", "").strip()
        price = item.get("price", "")
        if not description or not re.match(PRICE_REGEX, price):
            return f"Invalid item description or price for item: {description}", 400

    return None, 200  # Return success if validation passes

# Function to calculate points based on the receipt details
def calculate_points(receipt):
    points = 0  # Initialize points to 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    retailer_name = receipt.get("retailer", "")  # Extract retailer name from the receipt
    points += sum(1 for c in retailer_name if c.isalnum())  # Count alphanumeric characters and add to points

    # Rule 2: 50 points if the total is a round dollar amount (no cents)
    total = receipt.get("total", "0.00")  # Extract total from the receipt (default to "0.00" if not found)
    try:
        if float(total).is_integer():  # Check if total is an integer (round dollar amount)
            points += 50  # Add 50 points for round dollar amounts
    except ValueError:  # In case total cannot be converted to float
        pass

    # Rule 3: 25 points if the total is a multiple of 0.25
    try:
        if float(total) % 0.25 == 0:  # Check if total is divisible by 0.25
            points += 25  # Add 25 points for multiples of 0.25
    except ValueError:  # In case total cannot be converted to float
        pass

    # Rule 4: 5 points for every two items on the receipt
    items = receipt.get("items", [])  # Extract items list from the receipt (empty list if not found)
    points += (len(items) // 2) * 5  # For every two items, add 5 points

    # Rule 5: For each item, if the description's length is a multiple of 3, 
    # multiply the price by 0.2 and round up to the nearest integer.
    for item in items:  # Loop through each item in the list
        description = item.get("shortDescription", "").strip()  # Get the trimmed description of the item
        price = item.get("price", "0.00")  # Extract price (default to "0.00" if not found)
        if len(description) % 3 == 0:  # Check if the length of the description is divisible by 3
            try:
                price_points = int((float(price) * 0.2) + 0.9999)  # Calculate price points based on 0.2 multiplier, rounded up
                points += price_points  # Add calculated price points to total points
            except ValueError:  # In case price cannot be converted to float
                pass
    
    # Rule 6: 5 points if the total is greater than 10.00 (generated by a large language model)

    try:  # Begin a try block to handle any potential errors when converting the total to a float
    if float(total) > 10.00:  # Convert the 'total' value to a float and check if it is greater than 10.00
        points += 5  # Add 5 points to the total points if the condition is true
    except ValueError:  # Handle the case where the 'total' cannot be converted to a float (e.g., if it's invalid or missing)
        pass  # Silently ignore the error and continue execution

      
    # Rule 7: 6 points if the day of the purchase is odd
    purchase_date = receipt.get("purchaseDate", "")  # Extract purchase date (default to empty string if not found)
    try:
        day = int(purchase_date.split("-")[-1])  # Extract the day from the date (assumes format YYYY-MM-DD)
        if day % 2 != 0:  # Check if the day is odd
            points += 6  # Add 6 points for odd days
    except (ValueError, IndexError):  # In case of any parsing error
        pass

    # Rule 8: 10 points if the purchase time is between 2:00 PM and 4:00 PM
    purchase_time = receipt.get("purchaseTime", "")  # Extract purchase time (default to empty string if not found)
    try:
        purchase_time_obj = datetime.strptime(purchase_time, "%H:%M")  # Convert time string to datetime object
        if 14 <= purchase_time_obj.hour < 16:  # Check if the hour is between 2 PM and 4 PM
            points += 10  # Add 10 points if purchase time is in the range
    except ValueError:  # In case time cannot be parsed
        pass

    return points  # Return the total calculated points


# POST route for processing receipts
@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    try:
        receipt = request.json  # Get the JSON data from the incoming request
        if not receipt:  # Check if the receipt data is missing or invalid
            return jsonify({"error": "Invalid receipt data"}), 400  # Return a 400 error if invalid

         # Validate receipt data against the schema
        error_message, status_code = validate_receipt(receipt)
        if status_code != 200:
            return jsonify({"error": error_message}), status_code

        # Generate a unique ID for this receipt
        receipt_id = str(uuid.uuid4())  # Use UUID to generate a unique identifier

        # Calculate points for the receipt
        points = calculate_points(receipt)

        # Store the receipt and its calculated points in the in-memory storage
        receipts_data[receipt_id] = {
            "receipt": receipt,  # Store the original receipt data
            "points": points  # Store the calculated points for the receipt
        }

        return jsonify({"id": receipt_id}), 200  # Return the unique receipt ID and a 200 success status

    except Exception as e:  # Catch any unexpected errors
        return jsonify({"error": "An error occurred while processing the receipt"}), 500  # Return a 500 error for internal server errors


# GET route for retrieving points of a specific receipt by its ID
@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_receipt_points(receipt_id):
    receipt_entry = receipts_data.get(receipt_id)  # Retrieve the receipt data using the receipt ID

    if not receipt_entry:  # If the receipt is not found in the in-memory storage
        return jsonify({"error": "Receipt not found"}), 404  # Return a 404 error

    return jsonify({"points": receipt_entry["points"]}), 200  # Return the points of the receipt with a 200 success status


# Run the application on localhost with debugging enabled
if __name__ == '__main__':
    app.run(debug=True)

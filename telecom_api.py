# telecom_api.py

def simulate_telecom_api_request(phone_number):
    """
    Simulate a telecom API request (for testing).
    Example: Simulate checking if the phone number is valid.
    """
    if len(phone_number) == 10:  # Simulate a basic length check for phone numbers
        return {"status": "success", "message": "Number is valid"}
    else:
        return {"status": "error", "message": "Invalid number"}

def get_user(user_id: str) -> dict:
    """
    Simulates a database fetch for a user profile.
    """
    mock_db = {
        "user_1": {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "billing": {
                "stripe_id": "cus_987654321",
                "plan": "premium"
            }
        },
        "user_2": {
            "name": "Bob Jones",
            "email": "bob@example.com",
            "billing": {
                # BUG 2: Intentionally missing 'stripe_id' causing a deep KeyError
                "plan": "free"
            }
        }
    }
    
    # Return a default empty structure if user not found to simulate a real record
    return mock_db.get(user_id, {"name": "Unknown", "billing": {}})

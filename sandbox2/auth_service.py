from database_mock import get_user

def get_stripe_customer_id(user_id: str) -> str:
    """
    Validates the user token/ID and retrieves their Stripe Customer ID for billing.
    """
    user_data = get_user(user_id)
    
    # This will raise a KeyError if "stripe_id" is missing from the billing dictionary.
    # We intentionally do not use .get() here to simulate a deep KeyError bug.
    stripe_id = user_data["billing"]["stripe_id"]
    
    return stripe_id

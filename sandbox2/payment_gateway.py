from datetime import datetime

def calculate_discount(price, discount_rate=0.1):
    """
    Applies a discount to the given price.
    Expects a float or int.
    """
    # BUG 1: If 'price' is a string, this math operation will raise a TypeError
    discount_amount = price * discount_rate
    final_price = price - discount_amount
    return final_price

def process_refund(transaction_id: str):
    """
    Processes a refund for a given transaction.
    """
    # BUG 3: Shadowing the 'datetime' class with an instance of datetime!
    datetime = datetime.now()
    
    # The developer meant to parse a date using datetime.strptime,
    # but since 'datetime' is now an instance, it will raise:
    # AttributeError: 'datetime.datetime' object has no attribute 'strptime'
    formatted_date = datetime.strptime("2023-10-01", "%Y-%m-%d")
    
    return {
        "transaction": transaction_id, 
        "status": "REFUNDED",
        "processed_at": str(formatted_date)
    }

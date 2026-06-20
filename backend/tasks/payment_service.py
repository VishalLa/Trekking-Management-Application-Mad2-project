import time
from datetime import datetime

def payment(card_data: dict) -> bool:
    """
    Validates card data and simulates processing a payment.
    
    Expected card_data: 
    {
        'card_no': int, 
        'card_cvv': int,
        'price': float,
        'phone_no': int, 
        'expration_date': str, # Expected format 'MM/YY'
        'card_holder_name': str
    }
    """
    try:
        required_keys = ['card_no', 'card_cvv', 'price', 'phone_no', 'expration_date', 'card_holder_name']
        
        if not all(key in card_data for key in required_keys):
            print("Payment Failed: Missing required card data fields.")
            return False

        card_no = str(card_data['card_no'])
        cvv = str(card_data['card_cvv'])
        price = float(card_data['price'])
        phone_no = str(card_data['phone_no'])
        exp_date_str = str(card_data['expration_date']).strip()
        name = str(card_data['card_holder_name']).strip()

        if not (13 <= len(card_no) <= 19) or not card_no.isdigit():
            print("Payment Failed: Invalid card number.")
            return False
            
        if not (3 <= len(cvv) <= 4) or not cvv.isdigit():
            print("Payment Failed: Invalid CVV.")
            return False
            
        if price <= 0:
            print("Payment Failed: Invalid charge amount.")
            return False
            
        if not name:
            print("Payment Failed: Cardholder name is required.")
            return False

        try:
            exp_month, exp_year = map(int, exp_date_str.split('/'))
            exp_year += 2000
            
            now = datetime.now()
            current_month, current_year = now.month, now.year
            
            if not (1 <= exp_month <= 12):
                print("Payment Failed: Invalid expiration month.")
                return False
                
            if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
                print("Payment Failed: Card has expired.")
                return False
        except ValueError:
            print("Payment Failed: Invalid expiration date format. Use 'MM/YY'.")
            return False

        print(f"Initiating payment of ${price:.2f} for {name}...")
        time.sleep(1.5) 

        # random bank declines (1% of the time)
        import random
        if random.random() < 0.01:
            print("Payment Failed: Bank declined the transaction.")
            return False

        print("Payment Successful: Transaction approved!")
        return True

    except Exception as e:
        print(f"Payment Failed: An unexpected server error occurred -> {e}")
        return False
    
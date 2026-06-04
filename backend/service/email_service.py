def send_suspension_email(user_email, user_name):
    subject = "Important: Account Suspension and Booking Cancellation"
    body = f"Hello {user_name},\n\nYour account has been suspended. Any active trek bookings have been cancelled and refunded as per our policy."
    
    # TODO: 
    print(f"📧 EMAIL SENT TO: {user_email} | SUBJECT: {subject}")


def send_active_email(user_email, user_name):
    subject = "Important: Account Activation"
    # body = f"Hello {user_name},\n\nYour account has been suspended. Any active trek bookings have been cancelled and refunded as per our policy."
    
    # TODO: 
    print(f"📧 EMAIL SENT TO: {user_email} | SUBJECT: {subject}")


def send_trek_cancellation_email(user_email, user_name, trek_name, refund_amount):
    """
    Placeholder for email and refund gateway logic.
    """
    subject = f"Urgent: {trek_name} has been cancelled"
    body = f"Hello {user_name},\n\nWe regret to inform you that {trek_name} has been cancelled. A full refund of ₹{refund_amount} has been initiated to your original payment method."
    
    # TODO: Add real email sending / Stripe / Razorpay refund logic here!
    print(f"💸 REFUND ISSUED: ₹{refund_amount} to {user_name}")
    print(f"📧 EMAIL SENT TO: {user_email} | SUBJECT: {subject}")

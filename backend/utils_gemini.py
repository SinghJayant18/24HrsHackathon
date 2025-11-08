from datetime import datetime
from .settings import settings


def generate_email_content(prompt: str) -> str:
    """
    Best-effort Gemini integration; falls back to prompt if library or
    API key is not available.
    """
    try:
        import google.generativeai as genai

        if not settings.gemini_api_key:
            print("⚠️  Gemini API key not configured - using fallback content")
            return prompt
        
        print("🤖 Generating email content with Gemini API...")
        genai.configure(api_key=settings.gemini_api_key)
        
        # Try different models if one fails
        models_to_try = [settings.gemini_model, "gemini-pro", "gemini-1.5-pro"]
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                resp = model.generate_content(prompt)
                text = getattr(resp, "text", None)
                if text:
                    print(f"✅ Gemini content generated successfully using {model_name}")
                    return text
            except Exception as model_error:
                if model_name == models_to_try[-1]:
                    # Last model failed, raise the error
                    raise model_error
                print(f"⚠️  Model {model_name} failed, trying next...")
                continue
        
        print("⚠️  Gemini returned empty - using fallback")
        return prompt
    except Exception as e:
        print(f"❌ Gemini API error: {str(e)} - using fallback content")
        return prompt


def generate_order_status_email(
    customer_name: str,
    order_id: int,
    status: str,
    status_change_time: datetime,
    expected_delivery: str | None = None,
    total_amount: float | None = None,
    items_summary: str | None = None,
) -> str:
    """
    Generate professional order status email content using Gemini.
    """
    status_messages = {
        "placed": "Your order has been successfully placed!",
        "processing": "We're preparing your order for dispatch.",
        "dispatched": "Great news! Your order has been dispatched.",
        "delivered": "Your order has been delivered successfully!",
        "cancelled": "Your order has been cancelled.",
    }

    status_msg = status_messages.get(status.lower(), "Your order status has been updated.")

    time_str = status_change_time.strftime("%d %B %Y at %I:%M %p")

    prompt = f"""Write a professional, friendly email to customer {customer_name} about their order #{order_id}.

Status: {status.upper()}
Status Message: {status_msg}
Status Changed On: {time_str}
{f'Expected Delivery: {expected_delivery}' if expected_delivery else ''}
{f'Total Amount: ₹{total_amount:.2f}' if total_amount else ''}
{f'Items: {items_summary}' if items_summary else ''}

Write a warm, professional email that:
1. Addresses the customer by name
2. Clearly states the order status and what it means
3. Includes the date and time of the status change
4. {f'Mentions expected delivery date: {expected_delivery}' if expected_delivery else 'Mentions delivery timeline'}
5. {f'Includes order total: ₹{total_amount:.2f}' if total_amount else ''}
6. Provides next steps or reassurance
7. Ends with a thank you message

Keep it concise, professional, and customer-friendly. Return only the email body text (no subject line)."""

    content = generate_email_content(prompt)

    # Fallback if Gemini fails
    if content == prompt or not content:
        content = f"""
Dear {customer_name},

{status_msg}

Order Details:
- Order ID: #{order_id}
- Status: {status.upper()}
- Status Updated: {time_str}
{f'- Expected Delivery: {expected_delivery}' if expected_delivery else ''}
{f'- Total Amount: ₹{total_amount:.2f}' if total_amount else ''}

Thank you for your business!

Best regards,
Small Scale Business Automation Team
"""

    return content

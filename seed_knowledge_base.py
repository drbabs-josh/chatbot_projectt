"""
Seeds the KNOWLEDGE_BASE table with starter entries across the four
support domains described in Chapter Five, Section 5.6 (Billing and
Payments, Technical Troubleshooting, Account Management, General
Enquiries), and creates a default admin user.

Run from the project root:
    python data/seed_knowledge_base.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import KnowledgeBase, User

KB_ENTRIES = [
    # --- Billing and Payments ---
    ("check_invoice", "How do I check my invoice", "You can view and download your invoices from the Billing section of your account dashboard under 'Invoice History'.", "Billing and Payments"),
    ("check_invoice", "Where can I find my last bill", "Your most recent bill is available under Billing > Invoice History in your account dashboard.", "Billing and Payments"),
    ("check_invoice", "I need a copy of my receipt", "Receipts for all past payments can be downloaded as PDF from the Billing > Invoice History page.", "Billing and Payments"),

    ("payment_methods", "What payment methods do you accept", "We accept debit/credit cards, bank transfer, and USSD payments through our secure payment gateway.", "Billing and Payments"),
    ("payment_methods", "Can I pay with my card", "Yes, we accept Visa, Mastercard, and Verve cards for all payments.", "Billing and Payments"),
    ("payment_methods", "How do I update my payment card", "Go to Billing > Payment Methods and select 'Update Card' to enter your new card details securely.", "Billing and Payments"),

    ("refund_request", "How do I request a refund", "To request a refund, go to Billing > Transactions, select the payment in question, and click 'Request Refund'. Refunds are processed within 5-7 business days.", "Billing and Payments"),
    ("refund_request", "I was charged twice, can I get my money back", "We're sorry about that. Please submit a refund request from Billing > Transactions and our team will investigate and refund any duplicate charge within 5-7 business days.", "Billing and Payments"),
    ("refund_request", "When will my refund arrive", "Approved refunds are credited back to your original payment method within 5-7 business days.", "Billing and Payments"),

    ("billing_dispute", "I don't recognise a charge on my account", "Please open a billing dispute from Billing > Transactions so our team can investigate the charge and respond within 48 hours.", "Billing and Payments"),
    ("billing_dispute", "How do I dispute a transaction", "You can raise a dispute directly from the Transactions page by clicking 'Dispute this charge'. Our billing team reviews disputes within 48 hours.", "Billing and Payments"),
    ("billing_dispute", "This bill looks wrong", "I understand the concern. Please raise a billing dispute from your Transactions page and our billing team will review it within 48 hours.", "Billing and Payments"),

    ("subscription_cancel", "How do I cancel my subscription", "You can cancel anytime from Account > Subscription > Cancel Plan. Your access continues until the end of the current billing period.", "Billing and Payments"),
    ("subscription_cancel", "I want to stop my plan", "To stop your subscription, go to Account > Subscription and select 'Cancel Plan'. You'll keep access until the current period ends.", "Billing and Payments"),
    ("subscription_cancel", "Can I get a refund if I cancel", "Cancellations take effect at the end of the current billing period; we do not offer prorated refunds for partial periods.", "Billing and Payments"),

    # --- Technical Troubleshooting ---
    ("login_issue", "I can't log in to my account", "Please double-check your email and password. If the issue continues, use the 'Forgot Password' link on the login page to reset your credentials.", "Technical Troubleshooting"),
    ("login_issue", "My login keeps failing", "This is usually caused by an incorrect password or a temporary session issue. Try clearing your browser cache or resetting your password.", "Technical Troubleshooting"),
    ("login_issue", "It says my account doesn't exist", "Please confirm you're using the email address you registered with. If you still can't log in, contact support and we'll verify your account.", "Technical Troubleshooting"),

    ("app_crash", "The app keeps crashing", "Please try updating to the latest version of the app, and restart your device. If the crash continues, let us know your device model and OS version.", "Technical Troubleshooting"),
    ("app_crash", "The website is not loading properly", "Please try clearing your browser cache or using a different browser. If the issue persists, it may be a temporary server issue — please try again shortly.", "Technical Troubleshooting"),
    ("app_crash", "I'm getting an error message", "Could you share the exact error message you're seeing? In the meantime, try refreshing the page or restarting the app.", "Technical Troubleshooting"),

    ("slow_performance", "The system is very slow", "Slow performance is often related to network connectivity. Please check your internet connection, or try again during off-peak hours.", "Technical Troubleshooting"),
    ("slow_performance", "Pages are taking too long to load", "This can happen during high traffic periods. Please try refreshing the page, and let us know if the delay continues for more than a few minutes.", "Technical Troubleshooting"),
    ("slow_performance", "Why is everything lagging", "We apologise for the inconvenience. Please check your connection speed; if our servers are experiencing high load, performance should return to normal shortly.", "Technical Troubleshooting"),

    ("reset_password", "How do I reset my password", "Click 'Forgot Password' on the login page and follow the link sent to your registered email to set a new password.", "Technical Troubleshooting"),
    ("reset_password", "I forgot my password", "No problem — use the 'Forgot Password' option on the login screen, and we'll email you a secure reset link.", "Technical Troubleshooting"),
    ("reset_password", "The password reset email never arrived", "Please check your spam folder first. If it's not there after 10 minutes, contact support and we'll manually trigger a new reset email.", "Technical Troubleshooting"),

    ("connectivity_issue", "I keep getting disconnected", "Intermittent disconnections are usually due to unstable internet connectivity. Please check your Wi-Fi or mobile data signal and try reconnecting.", "Technical Troubleshooting"),
    ("connectivity_issue", "My session keeps timing out", "Sessions expire automatically after a period of inactivity for security reasons. Simply log in again to continue.", "Technical Troubleshooting"),
    ("connectivity_issue", "The chat is not connecting", "Please check your internet connection and refresh the page. If the problem continues, our servers may be temporarily unavailable.", "Technical Troubleshooting"),

    # --- Account Management ---
    ("update_profile", "How do I update my profile information", "Go to Account > Profile Settings to update your name, phone number, and other personal details at any time.", "Account Management"),
    ("update_profile", "I need to change my phone number", "You can update your phone number from Account > Profile Settings. A verification code will be sent to confirm the change.", "Account Management"),
    ("update_profile", "Can I update my address", "Yes, your address can be updated from Account > Profile Settings under the 'Address' section.", "Account Management"),

    ("change_email", "How do I change my email address", "Go to Account > Profile Settings > Email, enter your new email, and confirm it via the verification link sent to that address.", "Account Management"),
    ("change_email", "I no longer have access to my old email", "Please contact support directly with proof of identity so we can manually update your account email.", "Account Management"),
    ("change_email", "My email verification link expired", "No problem — go back to Account > Profile Settings > Email and click 'Resend Verification Link'.", "Account Management"),

    ("delete_account", "How do I delete my account", "You can permanently delete your account from Account > Settings > Delete Account. Please note this action cannot be undone.", "Account Management"),
    ("delete_account", "I want to close my account permanently", "Account deletion is available under Account > Settings > Delete Account. All your data will be permanently removed after confirmation.", "Account Management"),
    ("delete_account", "Can I recover my account after deleting it", "Unfortunately, account deletion is permanent and cannot be reversed. Please make sure to back up any data you need beforehand.", "Account Management"),

    ("two_factor_setup", "How do I enable two-factor authentication", "Go to Account > Security > Two-Factor Authentication and follow the prompts to link an authenticator app or your phone number.", "Account Management"),
    ("two_factor_setup", "Can I turn on extra login security", "Yes, two-factor authentication can be enabled from Account > Security for an extra layer of protection.", "Account Management"),
    ("two_factor_setup", "I lost access to my authenticator app", "Please contact support with proof of identity so we can help you disable two-factor authentication and set it up again.", "Account Management"),

    ("account_locked", "My account has been locked", "Accounts are temporarily locked after multiple failed login attempts. Please wait 15 minutes and try again, or reset your password.", "Account Management"),
    ("account_locked", "Why can't I access my account", "This may be due to a temporary security lock. Please reset your password or contact support if the issue continues.", "Account Management"),
    ("account_locked", "How do I unlock my account", "Resetting your password via the 'Forgot Password' link will automatically unlock your account.", "Account Management"),

    # --- General Enquiries ---
    ("business_hours", "What are your business hours", "Our support team is available Monday to Friday, 8:00 AM to 6:00 PM. The chatbot is available 24/7 for common questions.", "General Enquiries"),
    ("business_hours", "Are you open on weekends", "Our human support agents are available Monday to Friday. This chatbot, however, is available around the clock.", "General Enquiries"),
    ("business_hours", "When can I reach a live agent", "Live agents are available Monday to Friday, 8:00 AM to 6:00 PM. Outside these hours, I'm happy to help with common questions.", "General Enquiries"),

    ("contact_human", "I want to speak to a human agent", "Sure — I'm connecting you with a member of our support team now. They'll follow up with you shortly.", "General Enquiries"),
    ("contact_human", "Can I talk to a real person", "Of course. I'll escalate this conversation to a human support agent right away.", "General Enquiries"),
    ("contact_human", "This bot isn't helping, I need a person", "I understand — I'm escalating your request to a human agent now so they can assist you directly.", "General Enquiries"),

    ("service_availability", "Is your service available in my area", "Our service is currently available across Nigeria. Let us know your location and we can confirm specific coverage details.", "General Enquiries"),
    ("service_availability", "Do you operate outside Nigeria", "At the moment, our service is focused on the Nigerian market, with plans to expand in the future.", "General Enquiries"),
    ("service_availability", "Is the app available on both Android and iOS", "Yes, our app is available for download on both Android and iOS app stores.", "General Enquiries"),

    ("pricing_info", "How much does this cost", "Pricing depends on the plan you choose. Please visit our Pricing page for a full breakdown of available plans and features.", "General Enquiries"),
    ("pricing_info", "Do you have a free plan", "Yes, we offer a free tier with basic features. You can upgrade to a paid plan at any time from Account > Subscription.", "General Enquiries"),
    ("pricing_info", "What's included in the premium plan", "The premium plan includes priority support, advanced features, and higher usage limits. Full details are on our Pricing page.", "General Enquiries"),

    ("company_location", "Where are you located", "Our head office is located in Lagos, Nigeria, with support staff serving customers nationwide.", "General Enquiries"),
    ("company_location", "Do you have a physical office I can visit", "Yes, our office is in Lagos. Please contact support in advance to schedule a visit.", "General Enquiries"),
    ("company_location", "What company runs this service", "This service is operated as part of a customer support automation project. Contact support for further company details.", "General Enquiries"),
]


def main():
    app = create_app()
    with app.app_context():
        if KnowledgeBase.query.count() == 0:
            for intent, question, answer, category in KB_ENTRIES:
                db.session.add(KnowledgeBase(
                    intent_label=intent, question=question, answer=answer, category=category
                ))
            db.session.commit()
            print(f"Seeded {len(KB_ENTRIES)} knowledge base entries.")
        else:
            print(f"Knowledge base already has {KnowledgeBase.query.count()} entries — skipped seeding.")

        if User.query.filter_by(username="admin").first() is None:
            admin_password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
            db.session.add(User(
                username="admin",
                password_hash=generate_password_hash(admin_password),
                role="admin",
            ))
            db.session.commit()
            print(f"Created default admin user: admin / {admin_password}  (change this immediately)")
        else:
            print("Admin user already exists — skipped.")


if __name__ == "__main__":
    main()

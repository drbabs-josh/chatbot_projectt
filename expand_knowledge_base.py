"""
Adds additional paraphrased question variants to existing intents so the
classifier has enough examples per class to reach usable confidence
levels. Run AFTER data/seed_knowledge_base.py, before ml/train_classifier.py.

Run from the project root:
    python data/expand_knowledge_base.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import KnowledgeBase

EXTRA_ENTRIES = [
    ("check_invoice", "Where is my invoice history", "Your most recent bill is available under Billing > Invoice History in your account dashboard.", "Billing and Payments"),
    ("check_invoice", "Can you show me my past bills", "You can view and download your invoices from the Billing section under 'Invoice History'.", "Billing and Payments"),
    ("check_invoice", "I need proof of payment for last month", "Receipts for all past payments can be downloaded as PDF from Billing > Invoice History.", "Billing and Payments"),
    ("check_invoice", "How do I download my statement", "Your account statement can be downloaded from Billing > Invoice History as a PDF.", "Billing and Payments"),

    ("payment_methods", "Do you take bank transfer", "Yes, we accept bank transfer in addition to debit/credit cards and USSD payments.", "Billing and Payments"),
    ("payment_methods", "Is USSD payment supported", "Yes, USSD payments are supported alongside card and bank transfer options.", "Billing and Payments"),
    ("payment_methods", "How do I add a new card to my account", "Go to Billing > Payment Methods and select 'Add New Card' to securely save a new card for future payments.", "Billing and Payments"),
    ("payment_methods", "What cards can I use to pay", "We accept Visa, Mastercard, and Verve cards for all payments on the platform.", "Billing and Payments"),

    ("refund_request", "I want my money back for a cancelled order", "To request a refund, go to Billing > Transactions, select the payment, and click 'Request Refund'. This takes 5-7 business days.", "Billing and Payments"),
    ("refund_request", "How long does a refund take to process", "Approved refunds are credited back to your original payment method within 5-7 business days.", "Billing and Payments"),
    ("refund_request", "Can I get my payment reversed", "Yes, you can request a refund from Billing > Transactions. Processing takes 5-7 business days.", "Billing and Payments"),
    ("refund_request", "I paid for something I didn't receive", "We're sorry to hear that. Please submit a refund request from Billing > Transactions so we can investigate.", "Billing and Payments"),

    ("billing_dispute", "There's a charge I don't understand", "Please open a billing dispute from Billing > Transactions so our team can investigate and respond within 48 hours.", "Billing and Payments"),
    ("billing_dispute", "Someone else used my card on this platform", "Please raise a billing dispute immediately from Billing > Transactions. Our team will investigate within 48 hours.", "Billing and Payments"),
    ("billing_dispute", "I was overcharged", "I understand the concern. Please raise a billing dispute from your Transactions page for a review within 48 hours.", "Billing and Payments"),
    ("billing_dispute", "How do I report a wrong charge", "You can report and dispute a wrong charge directly from the Transactions page using the 'Dispute this charge' button.", "Billing and Payments"),

    ("subscription_cancel", "I don't want to renew my plan", "You can cancel anytime from Account > Subscription > Cancel Plan. Access continues until the current period ends.", "Billing and Payments"),
    ("subscription_cancel", "How do I turn off auto-renewal", "Go to Account > Subscription and disable 'Auto-Renew' to stop future automatic charges.", "Billing and Payments"),
    ("subscription_cancel", "Please cancel my membership", "To cancel, go to Account > Subscription > Cancel Plan. You'll retain access until the billing period ends.", "Billing and Payments"),
    ("subscription_cancel", "Do I get a prorated refund if I cancel early", "We do not offer prorated refunds; cancellation takes effect at the end of the current billing period.", "Billing and Payments"),

    ("login_issue", "I keep getting invalid credentials error", "Please double-check your email and password. If it persists, use 'Forgot Password' to reset your credentials.", "Technical Troubleshooting"),
    ("login_issue", "My account won't let me sign in", "This is usually due to an incorrect password or temporary session issue. Try resetting your password.", "Technical Troubleshooting"),
    ("login_issue", "Login page keeps refreshing without letting me in", "Please try clearing your browser cache and cookies, then attempt to log in again.", "Technical Troubleshooting"),
    ("login_issue", "I can't sign into my dashboard", "Please confirm you're using the correct registered email. If the issue continues, reset your password via the login page.", "Technical Troubleshooting"),

    ("app_crash", "The mobile app force closes", "Please update to the latest app version and restart your device. Let us know your device model if the crash continues.", "Technical Troubleshooting"),
    ("app_crash", "I get a white screen when I open the app", "Try force-closing and reopening the app, or reinstalling it. Let us know if a white screen keeps appearing.", "Technical Troubleshooting"),
    ("app_crash", "The site froze and won't respond", "Please try refreshing the page or clearing your browser cache. If it persists, there may be a temporary server issue.", "Technical Troubleshooting"),
    ("app_crash", "I got a 500 internal server error", "This indicates a temporary server-side issue. Please try again in a few minutes; contact support if it continues.", "Technical Troubleshooting"),

    ("slow_performance", "Why does the dashboard take forever to load", "Slow loading is often related to network connectivity. Please check your connection or try again during off-peak hours.", "Technical Troubleshooting"),
    ("slow_performance", "The chatbot is responding really slowly", "We apologise for the delay. This can happen during high traffic; please try again shortly.", "Technical Troubleshooting"),
    ("slow_performance", "Everything is loading at a snail's pace", "Please check your internet connection speed. If our servers are under high load, performance should improve shortly.", "Technical Troubleshooting"),
    ("slow_performance", "Response times feel very sluggish today", "We're sorry for the inconvenience. Try refreshing the page; if the delay continues, let us know the time it occurred.", "Technical Troubleshooting"),

    ("reset_password", "How can I set a new password", "Click 'Forgot Password' on the login page and follow the link sent to your email to set a new password.", "Technical Troubleshooting"),
    ("reset_password", "I need to change my password", "You can change your password anytime from Account > Security, or use 'Forgot Password' if you're logged out.", "Technical Troubleshooting"),
    ("reset_password", "The reset link isn't working", "Please request a new reset link from the login page; the previous link may have expired after 24 hours.", "Technical Troubleshooting"),
    ("reset_password", "I never got the password reset code", "Please check your spam folder. If it's not there after 10 minutes, contact support to resend the reset email.", "Technical Troubleshooting"),

    ("connectivity_issue", "The app disconnects randomly", "Intermittent disconnections are usually due to unstable internet connectivity. Please check your signal and reconnect.", "Technical Troubleshooting"),
    ("connectivity_issue", "I got logged out for no reason", "Sessions expire automatically after a period of inactivity for security. Simply log in again to continue.", "Technical Troubleshooting"),
    ("connectivity_issue", "Chat messages aren't sending", "Please check your internet connection and refresh the page. Our servers may be temporarily unavailable.", "Technical Troubleshooting"),
    ("connectivity_issue", "My connection to support keeps dropping", "This is often caused by unstable Wi-Fi or mobile data. Please check your connection and try reconnecting.", "Technical Troubleshooting"),

    ("update_profile", "I need to update my personal details", "Go to Account > Profile Settings to update your name, phone number, and other details anytime.", "Account Management"),
    ("update_profile", "How do I change my display name", "You can update your display name from Account > Profile Settings.", "Account Management"),
    ("update_profile", "Can I edit my delivery address", "Yes, your address can be updated from Account > Profile Settings under the 'Address' section.", "Account Management"),
    ("update_profile", "Where do I update my contact information", "All contact information can be updated from Account > Profile Settings.", "Account Management"),

    ("change_email", "I want to switch to a new email address", "Go to Account > Profile Settings > Email, enter the new email, and confirm via the verification link sent to it.", "Account Management"),
    ("change_email", "My email address changed, how do I update it here", "Update your email from Account > Profile Settings > Email, then verify it using the link we send you.", "Account Management"),
    ("change_email", "Can support change my email for me", "For security, please contact support with proof of identity so we can manually update your account email.", "Account Management"),
    ("change_email", "The verification code for my new email expired", "Go back to Account > Profile Settings > Email and click 'Resend Verification Link' to get a new code.", "Account Management"),

    ("delete_account", "I want to permanently remove my account", "You can permanently delete your account from Account > Settings > Delete Account. This cannot be undone.", "Account Management"),
    ("delete_account", "How do I deactivate my profile forever", "Account deletion is available under Account > Settings > Delete Account, and is permanent once confirmed.", "Account Management"),
    ("delete_account", "Please erase all my data", "You can request full account and data deletion from Account > Settings > Delete Account.", "Account Management"),
    ("delete_account", "Is account deletion reversible", "No, account deletion is permanent and cannot be reversed. Please back up any data you need first.", "Account Management"),

    ("two_factor_setup", "How do I add extra security to my login", "Go to Account > Security > Two-Factor Authentication and follow the prompts to enable it.", "Account Management"),
    ("two_factor_setup", "Can I use an authenticator app for login", "Yes, you can link an authenticator app under Account > Security > Two-Factor Authentication.", "Account Management"),
    ("two_factor_setup", "How do I turn off two-factor authentication", "Go to Account > Security and disable Two-Factor Authentication; you may be asked to verify your identity first.", "Account Management"),
    ("two_factor_setup", "I want SMS codes for login verification", "You can enable SMS-based two-factor authentication from Account > Security using your registered phone number.", "Account Management"),

    ("account_locked", "It says too many failed attempts", "Accounts are temporarily locked after multiple failed login attempts. Please wait 15 minutes and try again.", "Account Management"),
    ("account_locked", "I'm locked out of my profile", "This may be a temporary security lock. Please reset your password or contact support if it continues.", "Account Management"),
    ("account_locked", "My account got suspended, why", "A temporary lock usually follows multiple failed logins. Resetting your password will normally unlock your account.", "Account Management"),
    ("account_locked", "How long does an account lock last", "Account locks are usually lifted automatically after 15 minutes, or immediately after a successful password reset.", "Account Management"),

    ("business_hours", "What time do you close", "Our support team is available Monday to Friday, 8:00 AM to 6:00 PM. The chatbot is available 24/7.", "General Enquiries"),
    ("business_hours", "Are you open right now", "This chatbot is available 24/7. Our human support team is available Monday to Friday, 8:00 AM to 6:00 PM.", "General Enquiries"),
    ("business_hours", "What days do you work", "Our support team works Monday through Friday, 8:00 AM to 6:00 PM.", "General Enquiries"),
    ("business_hours", "Do you have holiday hours", "During public holidays, our human support team may be unavailable, but this chatbot remains available 24/7.", "General Enquiries"),

    ("contact_human", "Please connect me with support staff", "Sure — I'm connecting you with a member of our support team now. They'll follow up shortly.", "General Enquiries"),
    ("contact_human", "Get me a real agent now", "I understand — I'm escalating your request to a human agent right away.", "General Enquiries"),
    ("contact_human", "I don't want to talk to a bot anymore", "That's okay, I'm escalating this conversation to a human support agent now.", "General Enquiries"),
    ("contact_human", "Transfer me to customer service", "Sure thing — transferring you to a human customer service agent now.", "General Enquiries"),

    ("service_availability", "Do you serve customers outside Lagos", "Yes, our service is available across Nigeria, not just Lagos.", "General Enquiries"),
    ("service_availability", "Can people in other countries use this", "Currently our service is focused on the Nigerian market, with plans to expand in future.", "General Enquiries"),
    ("service_availability", "Is there an iOS version of the app", "Yes, our app is available on both the Apple App Store and Google Play Store.", "General Enquiries"),
    ("service_availability", "Which regions do you currently support", "We currently operate across Nigeria, with support available nationwide.", "General Enquiries"),

    ("pricing_info", "What are your plan prices", "Pricing depends on the plan you choose. Please visit our Pricing page for a full breakdown.", "General Enquiries"),
    ("pricing_info", "Is there a discount for annual billing", "Yes, annual plans typically come with a discount compared to monthly billing. See our Pricing page for details.", "General Enquiries"),
    ("pricing_info", "What do I get if I upgrade my plan", "Upgrading unlocks priority support, advanced features, and higher usage limits. Full details are on our Pricing page.", "General Enquiries"),
    ("pricing_info", "Can I try it for free first", "Yes, we offer a free tier with basic features so you can try the service before upgrading.", "General Enquiries"),

    ("company_location", "What city are you based in", "Our head office is located in Lagos, Nigeria, with support staff serving customers nationwide.", "General Enquiries"),
    ("company_location", "Can I visit your office in person", "Yes, our office is in Lagos. Please contact support in advance to schedule a visit.", "General Enquiries"),
    ("company_location", "Who owns this platform", "This service is operated as part of a customer support automation project; contact support for further details.", "General Enquiries"),
    ("company_location", "Is your company registered in Nigeria", "Yes, our operations are based in and registered within Nigeria, headquartered in Lagos.", "General Enquiries"),
]


def main():
    app = create_app()
    with app.app_context():
        added = 0
        for intent, question, answer, category in EXTRA_ENTRIES:
            exists = KnowledgeBase.query.filter_by(intent_label=intent, question=question).first()
            if not exists:
                db.session.add(KnowledgeBase(
                    intent_label=intent, question=question, answer=answer, category=category
                ))
                added += 1
        db.session.commit()
        total = KnowledgeBase.query.count()
        print(f"Added {added} new entries. Knowledge base now has {total} entries total.")


if __name__ == "__main__":
    main()

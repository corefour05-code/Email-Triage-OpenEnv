EMAILS = [
    {
        "email_id": "E001",
        "subject": "PRODUCTION DOWN - API returning 500 errors",
        "sender": "devops@clientcorp.com",
        "body": (
            "Our entire production environment is down. The API has been returning "
            "500 errors for the past 30 minutes. We have 10,000 users affected and "
            "are losing $5,000 per minute. Please respond IMMEDIATELY. "
            "We need an engineer on this NOW."
        ),
        "timestamp": "2024-03-15T09:02:00Z",
        "priority": "URGENT",
        "department": "Engineering",
        "reply_keywords": ["escalate", "engineer", "investigating", "priority", "immediately"],
    },
    {
        "email_id": "E002",
        "subject": "Invoice #4521 seems incorrect",
        "sender": "accounts@retailplus.com",
        "body": (
            "Hi, I was reviewing invoice #4521 dated Feb 28 and the amount "
            "charged ($2,340) doesn't match our agreed rate of $1,980/month. "
            "Could you please look into this and send a corrected invoice? "
            "Our payment is due next week. Thanks."
        ),
        "timestamp": "2024-03-15T10:15:00Z",
        "priority": "NORMAL",
        "department": "Billing",
        "reply_keywords": ["invoice", "review", "correct", "apologize", "billing team"],
    },
    {
        "email_id": "E003",
        "subject": "Interested in Enterprise Plan",
        "sender": "cto@startupxyz.io",
        "body": (
            "Hello, we're a Series B startup with 200 employees and we're evaluating "
            "your Enterprise plan. We'd love to schedule a demo and understand custom "
            "pricing. We are comparing with two other vendors and need to make a "
            "decision by end of month."
        ),
        "timestamp": "2024-03-15T11:00:00Z",
        "priority": "URGENT",
        "department": "Sales",
        "reply_keywords": ["demo", "schedule", "enterprise", "pricing", "sales team"],
    },
    {
        "email_id": "E004",
        "subject": "Can't reset my password",
        "sender": "user.jane@gmail.com",
        "body": (
            "I've been trying to reset my password for the last hour. "
            "I click the reset link in the email but it says 'link expired'. "
            "I've tried 3 times. My username is jane_doe_88. Please help!"
        ),
        "timestamp": "2024-03-15T11:30:00Z",
        "priority": "NORMAL",
        "department": "Support",
        "reply_keywords": ["password", "reset", "link", "support", "help"],
    },
    {
        "email_id": "E005",
        "subject": "Office holiday party feedback",
        "sender": "mark.jones@ourcompany.com",
        "body": (
            "Hey HR team, just wanted to say the holiday party last Friday was "
            "fantastic! The venue was great and everyone really enjoyed the team "
            "activities. One small suggestion - maybe next year we could include "
            "vegetarian options in the catering. Thanks for organizing it!"
        ),
        "timestamp": "2024-03-15T12:00:00Z",
        "priority": "LOW",
        "department": "HR",
        "reply_keywords": ["thank", "feedback", "noted", "appreciate"],
    },
    {
        "email_id": "E006",
        "subject": "URGENT: Data breach suspected - customer PII exposed",
        "sender": "security@partnerco.com",
        "body": (
            "We have detected unusual access patterns in our shared data pipeline "
            "that suggest a possible data breach. Customer PII including emails and "
            "phone numbers may have been exposed. Our legal team is involved. "
            "We need your security and engineering team on a call within the hour. "
            "This is a P0 incident."
        ),
        "timestamp": "2024-03-15T13:00:00Z",
        "priority": "URGENT",
        "department": "Engineering",
        "reply_keywords": ["security", "escalate", "incident", "engineering", "immediately", "call"],
    },
    {
        "email_id": "E007",
        "subject": "Request for product brochure",
        "sender": "procurement@bigretail.com",
        "body": (
            "Hello, we are exploring software solutions for our procurement team. "
            "Could you send us your latest product brochure and pricing sheet? "
            "We have a budget of around $50k/year. No rush on this."
        ),
        "timestamp": "2024-03-15T14:00:00Z",
        "priority": "NORMAL",
        "department": "Sales",
        "reply_keywords": ["brochure", "pricing", "sales", "send", "attach"],
    },
    {
        "email_id": "E008",
        "subject": "New employee onboarding - start date confirmed",
        "sender": "recruiter@hiringagency.com",
        "body": (
            "This is to confirm that Sarah Mitchell will be joining as a Senior "
            "Designer on April 1st. Please ensure her workstation, email, and "
            "system access are set up before her start date. Attached is her "
            "signed offer letter."
        ),
        "timestamp": "2024-03-15T15:00:00Z",
        "priority": "NORMAL",
        "department": "HR",
        "reply_keywords": ["onboarding", "confirm", "setup", "access", "ready"],
    },
    {
        "email_id": "E009",
        "subject": "Monthly newsletter subscription",
        "sender": "newsletter@industrydigest.com",
        "body": (
            "Thank you for subscribing to Industry Digest Monthly! "
            "Your first edition will arrive next Monday. "
            "You can manage your preferences at any time via your account portal."
        ),
        "timestamp": "2024-03-15T15:30:00Z",
        "priority": "LOW",
        "department": "None",
        "reply_keywords": [],
    },
    {
        "email_id": "E010",
        "subject": "Refund request - Order #78234",
        "sender": "angry.customer@hotmail.com",
        "body": (
            "I placed an order 3 weeks ago (Order #78234) and it still hasn't "
            "arrived. I've called support twice with no resolution. I am extremely "
            "frustrated and demand a full refund immediately. If this isn't resolved "
            "today I will dispute the charge with my bank and leave reviews on every "
            "platform I can find."
        ),
        "timestamp": "2024-03-15T16:00:00Z",
        "priority": "URGENT",
        "department": "Support",
        "reply_keywords": ["refund", "apologize", "order", "resolve", "escalate", "urgently"],
    },
]

EASY_EMAILS = EMAILS[:6]
MEDIUM_EMAILS = EMAILS[:8]
HARD_EMAILS = EMAILS

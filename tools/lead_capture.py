"""
tools/lead_capture.py
Mock lead capture tool for AutoStream agent.
"""

import json
import datetime


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """
    Mock API function to capture a qualified lead.
    In production, this would POST to a CRM like HubSpot, Salesforce, etc.

    Args:
        name: Full name of the lead
        email: Email address of the lead
        platform: Creator platform (YouTube, Instagram, TikTok, etc.)

    Returns:
        dict with success status and lead details
    """
    timestamp = datetime.datetime.now().isoformat()

    # Simulate CRM capture
    lead_data = {
        "status": "success",
        "lead_id": f"LEAD-{hash(email) % 100000:05d}",
        "name": name,
        "email": email,
        "platform": platform,
        "product_interest": "AutoStream Pro Plan",
        "captured_at": timestamp,
        "source": "Social-to-Lead Agent (Inflx)"
    }

    # Console log (as per assignment requirement)
    print(f"\n{'='*50}")
    print(f"✅ Lead captured successfully!")
    print(f"   Name     : {name}")
    print(f"   Email    : {email}")
    print(f"   Platform : {platform}")
    print(f"   Lead ID  : {lead_data['lead_id']}")
    print(f"   Time     : {timestamp}")
    print(f"{'='*50}\n")

    return lead_data

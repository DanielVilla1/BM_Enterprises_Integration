# ===== AI GENERATED: clerk_user =====
# Purpose: Shared rule for reading a Clerk user's verified primary email
# Inputs: Clerk user object (webhook data or Backend API user)
# Returns: the verified primary email, or None
# Flow:
# 1. Find the address whose id equals primary_email_address_id
# 2. Accept it only when its verification status is "verified"


def verified_primary_email(clerk_user: dict[str, object]) -> str | None:
    """Return the verified primary email address of a Clerk user, if any."""
    primary_id = clerk_user.get("primary_email_address_id")
    addresses = clerk_user.get("email_addresses")
    if not isinstance(addresses, list):
        return None
    for address in addresses:
        if not isinstance(address, dict) or address.get("id") != primary_id:
            continue
        verification = address.get("verification")
        email = address.get("email_address")
        is_verified = isinstance(verification, dict) and verification.get("status") == "verified"
        if is_verified and isinstance(email, str) and email:
            return email
    return None

#!/usr/bin/env python3
"""
Helper script to encode credentials.json to base64 for Render deployment.
Run this locally, then copy the output to your Render environment variables.
"""

import base64
import os
import secrets


def main():
    # Check for credentials file
    if not os.path.exists("credentials.json"):
        print("Error: credentials.json not found in current directory")
        return

    # Read and encode credentials
    with open("credentials.json", "rb") as f:
        creds_bytes = f.read()

    encoded = base64.b64encode(creds_bytes).decode("utf-8")

    # Generate a secure random token
    secret_token = secrets.token_urlsafe(32)

    print("=" * 60)
    print("RENDER ENVIRONMENT VARIABLES")
    print("=" * 60)
    print("\nCopy these values to your Render dashboard:\n")

    print("1. GOOGLE_CREDENTIALS_BASE64:")
    print("-" * 40)
    print(encoded)
    print("-" * 40)

    print("\n2. SECRET_TOKEN (your private URL token):")
    print("-" * 40)
    print(secret_token)
    print("-" * 40)

    print("\n" + "=" * 60)
    print("After deploying, your trigger URL will be:")
    print(f"https://YOUR-APP-NAME.onrender.com/run/{secret_token}")
    print("=" * 60)


if __name__ == "__main__":
    main()

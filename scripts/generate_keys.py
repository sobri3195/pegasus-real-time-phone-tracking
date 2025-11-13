#!/usr/bin/env python3
import os
import secrets

def generate_keys():
    print("=== Generating Security Keys ===\n")
    
    secret_key = secrets.token_urlsafe(32)
    print(f"SECRET_KEY={secret_key}")
    
    jwt_secret = secrets.token_urlsafe(32)
    print(f"JWT_SECRET={jwt_secret}")
    
    encryption_key = secrets.token_hex(32)
    print(f"ENCRYPTION_KEY={encryption_key}")
    
    print("\n=== Instructions ===")
    print("1. Copy the keys above to your .env file")
    print("2. Keep these keys secure and never commit them to git")
    print("3. Use different keys for production and development")
    print("4. Regenerate keys regularly for enhanced security")

if __name__ == '__main__':
    generate_keys()

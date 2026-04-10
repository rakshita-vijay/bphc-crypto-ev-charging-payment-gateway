# EV Charging Payment Gateway
## Secure Centralized Payment System using Post-Quantum & Lightweight Cryptography

### Project Overview

This is a comprehensive digital transaction system for purchasing electric vehicle (EV) charging time securely and verifiably. The system integrates three critical security technologies:

1. **Lightweight Cryptography (ASCON)** - Fast encryption for IoT/low-power devices
2. **Quantum Cryptography Awareness** - Demonstrates RSA vulnerability via Shor's Algorithm
3. **Blockchain Ledger** - Immutable transaction records

### System Architecture

### Key Components

1. **Grid Authority** - Central banking terminal for energy administrators
2. **Franchise/Kiosk** - Automated dispenser at charging stations
3. **EV Owner Device** - User platform for initiating charges
4. **Blockchain Ledger** - Immutable transaction record

### Cryptographic Components

#### SHA-3 Hashing
- **Purpose**: Generate unique IDs and create transaction hashes
- **ID Generation**: Franchise ID (FID) and User ID (UID)
- **Blockchain**: Each transaction's ID is SHA-3 hash of its data
- **Security**: Tamper-proof transaction records

#### ASCON - Lightweight Cryptography
- **Purpose**: Encrypt Franchise IDs in QR codes
- **Advantage**: Fast encryption/decryption on low-power devices
- **Key**: `RaksAditPriyVeda` (shared among all kiosks)
- **Nonce**: Timestamp prevents replay attacks
- **Associated Data**: Timestamp is authenticated but not encrypted

#### RSA Encryption
- **Purpose**: Encrypt VMID and PIN during transmission
- **Key Size**: 7919 × 1009 = 7,990,271
- **Public Key (e, n)**: (65537, 7990271)
- **Vulnerability**: Breakable by Shor's Algorithm on quantum computers

### Payment Flow

### Edge Cases Handled

1. **Insufficient Balance**: User rejected if balance < charge amount
2. **Invalid PIN**: Transaction rejected with wrong PIN
3. **Expired QR Code**: Timestamp mismatch prevents replay attacks
4. **Tampered QR Code**: ASCON decryption fails or FID mismatch detected
5. **Hardware Failure**: If cable unlock fails after payment → auto-refund
6. **Unknown User/Franchise**: Transaction rejected if UID/FID not found

### Quantum Cryptography Vulnerability

**Shor's Algorithm** can break RSA encryption:

```python
# Classical approach (currently secure)
Time to break RSA-2048: ~300 trillion years

# Quantum approach (future threat)
Time to break RSA-2048: ~8 hours (with 20M qubit quantum computer)


#### How to run
# Clone repository
git clone <repo-url>
cd bphc-crypto-ev-charging-payment-gateway

# Install dependencies
pip install -r requirements.txt

# Run unit tests
python3 grid.py
python3 user.py
python3 franchise.py
python3 rsa.py

# Run integration tests
python3 test_integration.py
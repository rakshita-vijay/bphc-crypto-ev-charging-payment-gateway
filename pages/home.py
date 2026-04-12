"""
Home page - Project overview and system architecture
"""

import streamlit as st

def show():
    st.title("EV Charging Payment Gateway")
    
    st.markdown("""
    ### Secure Centralized Payment System using Post-Quantum & Lightweight Cryptography
    
    This is a comprehensive digital transaction system for purchasing electric vehicle 
    charging time securely and verifiably.
    """)
    
    # st.markdown("---")
    
    # System Architecture
    st.header("System Architecture")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Components")
        st.markdown("""
        **1. Grid Authority (Central Server)**
        - Manages user and franchise accounts
        - Validates transactions
        - Maintains blockchain ledger
        
        **2. Charging Kiosk (Station Hardware)**
        - Generates encrypted QR codes
        - Processes payments
        - Controls cable unlock mechanism
        
        **3. EV Owner Device (User)**
        - Scans QR codes
        - Initiates charging sessions
        - Enters payment details
        
        **4. Blockchain Ledger**
        - Records all transactions
        - Ensures immutability
        - Handles disputes/refunds
        """)
    
    # with col2:
    #     st.subheader("Data Flow")
    #     st.markdown("""
    #     ```
    #     User Device          Kiosk                Grid Authority
    #        |                  |                        |
    #        +--[Register]----->|-----[Register]-------->|
    #        |                  |                        |
    #        +--[Scan QR]------>|--[Verify]---->|        |
    #        |                  |                |       |
    #        +--[Payment]------>|--[Validate]--[+------->|
    #        |                  |     ↓         |        |
    #        |                  |<-[Approval]---+        |
    #        |                  |     ↓                  |
    #        |<--[Success]------+--[Blockchain Record]-->|
    #     ```
    #     """)
    
    # st.markdown("---")
    
    # Cryptography Used
    st.header("Cryptographic Components")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("SHA-3 Hashing")
        st.markdown("""
        **Used for:**
        - ID generation (UID, FID)
        - Transaction ID creation
        - Blockchain integrity
        """)
    
    with col2:
        st.subheader("ASCON LWC")
        st.markdown("""
        **Used for:**
        - QR code encryption
        - Lightweight/IoT devices
        - Fast encoding/decoding
        """)
    
    with col3:
        st.subheader("RSA Encryption")
        st.markdown("""
        **Used for:**
        - VMID transmission
        - PIN protection
        - (Breakable by Shor's)
        """)
    
    st.markdown("---")
    
    # Key Features
    st.header("Key Features")
    
    features = {
        "Security": "Multiple layers of encryption prevent unauthorized access",
        "Speed": "ASCON provides fast encryption for low-power devices",
        "Immutability": "Blockchain ensures all transactions are tamper-proof",
        "Refunds": "Automatic refunds triggered on hardware failures",
        "Replay Prevention": "Timestamps prevent QR code reuse attacks",
        "Decentralized": "Multiple energy providers supported"
    }
    
    for feature, description in features.items():
        st.markdown(f"**{feature}**: {description}")
    
    st.markdown("---")
    
    # Quick Start
    st.header("Quick Start Guide")
    
    with st.expander("1. Grid Authority Setup", expanded=False):
        st.markdown("""
        1. Go to **Grid Authority** page
        2. **Register Users**: Enter user details (name, phone, PIN, balance)
        3. **Register Franchises**: Enter franchise details (name, zone, password)
        4. View users and franchises in the registry
        """)
    
    with st.expander("2. Franchise/Kiosk Setup", expanded=False):
        st.markdown("""
        1. Go to **Franchise/Kiosk** page
        2. **Generate QR Code**: Creates encrypted VFID for users to scan
        3. **Display QR**: Show the generated QR code on kiosk screen
        4. Monitor transactions in real-time
        """)
    
    with st.expander("3. EV Owner Payment", expanded=False):
        st.markdown("""
        1. Go to **EV Owner** page
        2. **Scan QR Code**: Upload or scan the kiosk's QR code
        3. **Enter Details**: Input charge amount and PIN
        4. **Confirm Payment**: Initiate the charging session
        5. **View Status**: See if payment succeeded or failed
        """)
    
    with st.expander("4. Admin Analytics", expanded=False):
        st.markdown("""
        1. Go to **Admin Analytics** page
        2. **View Statistics**: Total users, franchises, transactions, revenue
        3. **Run Shor's Demo**: See quantum vulnerability demonstration
        4. **Verify Blockchain**: Check chain integrity for tampering
        """)
    
    st.markdown("---")
    
    # Security Highlights
    st.header("Security Highlights")
    
    st.info("""
    **Tamper-Proof QR Codes**
    - Encrypted with ASCON using franchise ID
    - Timestamp as nonce prevents replay attacks
    - Any modification detected during decryption
    """)
    
    st.info("""
    **Quantum Cryptography Awareness**
    - RSA keys demonstrated to be breakable by Shor's Algorithm
    - Shows classical cryptography vulnerability
    - Recommend post-quantum algorithms for future systems
    """)
    
    st.warning("""
    **Automatic Refund on Hardware Failure**
    - If payment succeeds but cable unlock fails
    - Automatic refund recorded on blockchain with dispute flag
    - User and franchise both notified
    """)
    
    st.markdown("---")
    
    # Assumptions
    # st.header("Project Assumptions")
    
    # st.markdown("""
    # 1. **Energy Units**: Charging amount and balance are in energy units (not currency)
    # 2. **PIN Storage**: PINs are stored as plain text (in production: use secure hash)
    # 3. **Shared Encryption Key**: All kioskssshare same ASCON key (in production: use key management)
    # 4. **In-Memory Storage**: All data is in-memory (in production: use persistent database)
    # 5. **Hardware Simulation**: Cable unlock is simulated (in production: real hardware control)
    # 6. **Network**: Assume reliable network communication
    # 7. **Timestamps**: Server-side timestamps prevent manipulation
    # """)
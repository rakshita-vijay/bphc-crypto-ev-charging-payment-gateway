import streamlit as st
import os
from PIL import Image

def show():
    st.title("🚗 EV Owner Dashboard")
    
    grid = st.session_state.grid
    
    if len(grid.users) == 0:
        st.error("No users registered. Please register as a user in Grid Authority first.")
        return
    
    tab1, tab2, tab3 = st.tabs([
        "💳 Initiate Payment",
        "🧾 Transaction History",
        "👤 Account Details"
    ])
    
    # Tab 1: Payment
    with tab1:
        st.subheader("Initiate Charging Payment")
        
        # Select user
        user_names = {u.u_name: uid for uid, u in grid.users.items()}
        selected_user_name = st.selectbox(
            "Select Your Account",
            options=list(user_names.keys()),
            key="select_user"
        )
        
        selected_uid = user_names[selected_user_name]
        user = grid.users[selected_uid]
        
        st.info(f"""
        **Your Account:**
        - Name: {user.u_name}
        - VMID: {user.vmid}
        - Available Balance: {user.u_balance:.2f} units
        """)
        
        # Upload QR code
        st.subheader("Step 1: Scan/Upload QR Code")
        qr_upload = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])
        
        if qr_upload:
            # Save uploaded file
            qr_path = os.path.join("qrcodes", qr_upload.name)
            os.makedirs("qrcodes", exist_ok=True)
            with open(qr_path, "wb") as f:
                f.write(qr_upload.getbuffer())
            
            st.image(qr_upload, caption="Uploaded QR Code", use_column_width=False, width=300)
        
        # Enter payment details
        st.subheader("Step 2: Enter Payment Details")
        col1, col2 = st.columns(2)
        
        with col1:
            charge_amount = st.number_input(
                "Charging Amount (Energy Units)",
                min_value=0.1,
                value=100.0,
                key="charge_amount"
            )
        
        with col2:
            pin = st.text_input("PIN", type="password", max_chars=4, key="payment_pin")
        
        # Submit payment
        st.subheader("Step 3: Submit Payment")
        
        if st.button("💳 Initiate Payment", key="btn_initiate_payment"):
            if not qr_upload or not pin:
                st.error("❌ Please upload QR code and enter PIN")
            elif charge_amount > user.u_balance:
                st.error(f"❌ Insufficient balance. You have {user.u_balance:.2f} units")
            else:
                try:
                    from kiosk import Kiosk
                    from franchise import Franchise
                    
                    # Find a franchise to process payment
                    if len(grid.franchises) == 0:
                        st.error("No franchises available")
                    else:
                        franchise = list(grid.franchises.values())[0]
                        kiosk = Kiosk(grid, franchise)
                        
                        # Generate payment payload
                        payload = user.charge_request(qr_upload.name, int(charge_amount))
                        
                        with st.spinner("Processing payment..."):
                            result = kiosk.process_payment(
                                qr_upload.name,
                                user.uid,
                                franchise.fid,
                                payload,
                                int(charge_amount)
                            )
                        
                        if result["success"]:
                            st.success(f"✓ Payment Successful!")
                            st.balloons()
                            st.info(f"""
                            **Transaction Details:**
                            - Amount Charged: {result['amount']:.2f} units
                            - Remaining Balance: {user.u_balance:.2f} units
                            - Transaction ID: {result['transaction_id'][:20] if result['transaction_id'] else 'N/A'}...
                            - Status: Cable unlocked - Charging active
                            """)
                        else:
                            st.error(f"✗ Payment Failed")
                            st.warning(f"Reason: {result['reason']}")
                            if result.get("refund"):
                                st.info("Refund has been automatically processed")
                
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Tab 2: Transaction History
    with tab2:
        st.subheader("Your Transaction History")
        
        if len(grid.users) == 0:
            st.info("No users registered")
        else:
            user_names = {u.u_name: uid for uid, u in grid.users.items()}
            selected_user_name = st.selectbox(
                "Select Account",
                options=list(user_names.keys()),
                key="select_user_history"
            )
            
            selected_uid = user_names[selected_user_name]
            user = grid.users[selected_uid]
            
            # Find transactions for this user
            user_transactions = [b for b in grid.blockchain if b["uid"] == selected_uid]
            
            if len(user_transactions) == 0:
                st.info(f"No transactions for {user.u_name} yet")
            else:
                transaction_data = []
                for txn in user_transactions:
                    franchise = next((f for f in grid.franchises.values() if f.fid == txn["fid"]), None)
                    franchise_name = franchise.f_name if franchise else "Unknown"
                    
                    transaction_data.append({
                        "Time": txn["timestamp"],
                        "Station": franchise_name,
                        "Amount": f"{txn['amount']:.2f}",
                        "Type": "Refund" if txn["dispute_flag"] else "Charge",
                        "Status": "↩️" if txn["dispute_flag"] else "✓"
                    })
                
                st.dataframe(transaction_data, use_container_width=True)
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_charged = sum(t["amount"] for t in user_transactions if not t["dispute_flag"])
                    st.metric("Total Charged", f"{total_charged:.2f} units")
                with col2:
                    total_refunded = sum(t["amount"] for t in user_transactions if t["dispute_flag"])
                    st.metric("Total Refunded", f"{total_refunded:.2f} units")
                with col3:
                    st.metric("Transaction Count", len(user_transactions))
    
    # Tab 3: Account Details
    with tab3:
        st.subheader("Your Account Details")
        
        if len(grid.users) == 0:
            st.info("No users registered")
        else:
            user_names = {u.u_name: uid for uid, u in grid.users.items()}
            selected_user_name = st.selectbox(
                "Select Account",
                options=list(user_names.keys()),
                key="select_user_account"
            )
            
            selected_uid = user_names[selected_user_name]
            user = grid.users[selected_uid]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Name", user.u_name)
                st.metric("Phone", user.u_phone)
                st.metric("UID", user.uid)
            
            with col2:
                st.metric("Current Balance", f"{user.u_balance:.2f} units")
                st.metric("VMID", user.vmid[:25] + "...")
                st.metric("PIN", "••••" if user.u_pin else "Not set")
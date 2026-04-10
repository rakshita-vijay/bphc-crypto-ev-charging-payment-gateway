"""
Grid Authority Page - User and Franchise Management
"""

import streamlit as st
from grid import Grid
from user import User
from franchise import Franchise
from tabulate import tabulate

def show():
    st.title("🏛️ Grid Authority Dashboard")
    
    grid = st.session_state.grid
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Register User",
        "🏪 Register Franchise",
        "👥 View Users",
        "🏢 View Franchises",
        "📊 View Blockchain"
    ])
    
    # Tab 1: Register User
    with tab1:
        st.subheader("Register New EV Owner")
        
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("User Name", key="user_name")
            user_phone = st.text_input("Phone Number", key="user_phone", placeholder="9000000000")
        
        with col2:
            user_pin = st.text_input("PIN", type="password", key="user_pin", max_chars=4)
            user_balance = st.number_input("Initial Balance (Energy Units)", min_value=0.0, value=1000.0, key="user_balance")
        
        if st.button("Register User", key="btn_register_user"):
            if not user_name or not user_phone or not user_pin:
                st.error("❌ All fields are required")
            else:
                try:
                    # Create user
                    new_user = User(user_name, user_phone, user_pin, grid, user_balance)
                    
                    if new_user.uid:
                        st.success(f"✓ User registered successfully!")
                        st.info(f"""
                        **User Details:**
                        - UID: `{new_user.uid}`
                        - VMID: `{new_user.vmid}`
                        - Balance: {new_user.u_balance} units
                        """)
                        st.balloons()
                    else:
                        st.error("❌ User registration failed")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Tab 2: Register Franchise
    with tab2:
        st.subheader("Register New Charging Station Franchise")
        
        col1, col2 = st.columns(2)
        with col1:
            franchise_name = st.text_input("Franchise Name", key="franchise_name")
            franchise_acc = st.text_input("Account Number", key="franchise_acc")
        
        with col2:
            franchise_zone = st.selectbox(
                "Zone Code",
                options=["Z1", "Z2", "Z3"],
                key="franchise_zone"
            )
            franchise_pwd = st.text_input("Password", type="password", key="franchise_pwd")
        
        franchise_balance = st.number_input("Initial Balance (Energy Units)", min_value=0.0, value=500.0, key="franchise_balance")
        
        if st.button("Register Franchise", key="btn_register_franchise"):
            if not franchise_name or not franchise_acc or not franchise_pwd:
                st.error("❌ All fields are required")
            else:
                try:
                    new_franchise = Franchise(
                        franchise_name,
                        franchise_acc,
                        franchise_zone,
                        franchise_pwd,
                        franchise_balance,
                        grid
                    )
                    
                    if new_franchise.fid:
                        st.success(f"✓ Franchise registered successfully!")
                        st.info(f"""
                        **Franchise Details:**
                        - FID: `{new_franchise.fid}`
                        - Zone: {new_franchise.f_zone_code}
                        - Balance: {new_franchise.f_balance} units
                        """)
                        st.balloons()
                    else:
                        st.error("❌ Franchise registration failed (check zone code)")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Tab 3: View Users
    with tab3:
        st.subheader("Registered Users")
        
        if len(grid.users) == 0:
            st.info("No users registered yet")
        else:
            user_data = []
            for user in grid.users.values():
                user_data.append({
                    "UID": user.uid[:10] + "...",
                    "Name": user.u_name,
                    "Phone": user.u_phone,
                    "Balance": f"{user.u_balance:.2f}",
                    "VMID": user.vmid[:15] + "..."
                })
            
            st.dataframe(user_data, use_container_width=True)
            st.metric("Total Users", len(grid.users))
    
    # Tab 4: View Franchises
    with tab4:
        st.subheader("Registered Franchises")
        
        if len(grid.franchises) == 0:
            st.info("No franchises registered yet")
        else:
            franchise_data = []
            for franchise in grid.franchises.values():
                franchise_data.append({
                    "FID": franchise.fid[:10] + "...",
                    "Name": franchise.f_name,
                    "Zone": franchise.f_zone_code,
                    "Balance": f"{franchise.f_balance:.2f}",
                    "Provider": grid.zones.get(franchise.f_zone_code, "Unknown")
                })
            
            st.dataframe(franchise_data, use_container_width=True)
            st.metric("Total Franchises", len(grid.franchises))
    
    # Tab 5: View Blockchain
    with tab5:
        st.subheader("Transaction Blockchain Ledger")
        
        if len(grid.blockchain) == 0:
            st.info("No transactions recorded yet")
        else:
            blockchain_data = []
            for i, block in enumerate(grid.blockchain):
                blockchain_data.append({
                    "#": i + 1,
                    "TxnID": block["transaction_id"][:10] + "...",
                    "UID": block["uid"][:10] + "...",
                    "FID": block["fid"][:10] + "...",
                    "Amount": f"{block['amount']:.2f}",
                    "Dispute": "Yes" if block["dispute_flag"] else "No",
                    "Timestamp": block["timestamp"]
                })
            
            st.dataframe(blockchain_data, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Transactions", len(grid.blockchain))
            with col2:
                total_amount = sum(b["amount"] for b in grid.blockchain if not b["dispute_flag"])
                st.metric("Total Revenue", f"{total_amount:.2f} units")
            with col3:
                disputes = sum(1 for b in grid.blockchain if b["dispute_flag"])
                st.metric("Refund Blocks", disputes)
            
            # Blockchain Integrity Check
            st.markdown("---")
            st.subheader("Blockchain Integrity Verification")
            
            if st.button("Verify Chain Integrity", key="btn_verify_chain"):
                with st.spinner("Verifying blockchain..."):
                    is_valid = grid.verify_chain()
                
                if is_valid:
                    st.success("✓ Blockchain is intact and unmodified")
                else:
                    st.error("✗ Blockchain has been tampered with!")
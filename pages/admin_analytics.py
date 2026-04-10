"""
Admin Analytics Page - Statistics, Demos, and Verification
"""

import streamlit as st

def show():
    st.title("📊 Admin Analytics Dashboard")
    
    grid = st.session_state.grid
    
    tab1, tab2, tab3 = st.tabs([
        "📈 Statistics",
        "⚛️ Quantum Demo",
        "🔐 Blockchain Verification"
    ])
    
    # Tab 1: Statistics
    with tab1:
        st.subheader("System Statistics")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(grid.users))
        with col2:
            st.metric("Total Franchises", len(grid.franchises))
        with col3:
            st.metric("Total Transactions", len(grid.blockchain))
        with col4:
            total_revenue = sum(b["amount"] for b in grid.blockchain if not b["dispute_flag"])
            st.metric("Total Revenue", f"{total_revenue:.2f} units")
        
        # Detailed Statistics
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Statistics")
            total_user_balance = sum(u.u_balance for u in grid.users.values())
            average_balance = total_user_balance / len(grid.users) if grid.users else 0
            
            st.metric("Total User Balance", f"{total_user_balance:.2f} units")
            st.metric("Average User Balance", f"{average_balance:.2f} units")
            st.metric("Registered Users", len(grid.users))
        
        with col2:
            st.subheader("Franchise Statistics")
            total_franchise_balance = sum(f.f_balance for f in grid.franchises.values())
            average_franchise_balance = total_franchise_balance / len(grid.franchises) if grid.franchises else 0
            
            st.metric("Total Franchise Balance", f"{total_franchise_balance:.2f} units")
            st.metric("Average Franchise Balance", f"{average_franchise_balance:.2f} units")
            st.metric("Registered Franchises", len(grid.franchises))
        
        # Transaction Details
        st.markdown("---")
        st.subheader("Transaction Breakdown")
        
        col1, col2, col3 = st.columns(3)
        
        successful_txns = sum(1 for b in grid.blockchain if not b["dispute_flag"])
        refund_txns = sum(1 for b in grid.blockchain if b["dispute_flag"])
        
        with col1:
            st.metric("Successful Transactions", successful_txns)
        with col2:
            st.metric("Refund Transactions", refund_txns)
        with col3:
            success_rate = (successful_txns / len(grid.blockchain) * 100) if grid.blockchain else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Tab 2: Quantum Vulnerability Demo
    with tab2:
        st.subheader("⚛️ Quantum Cryptography Vulnerability Demo")
        
        st.warning("""
        This demonstration shows how Shor's Algorithm can break RSA encryption.
        
        **Why this matters:**
        - RSA is used for VMID and PIN encryption in this system
        - Shor's algorithm on a quantum computer can factorize large numbers efficiently
        - Classical computers would take thousands of years to do this
        - Quantum computers can do it in polynomial time
        """)
        
        st.markdown("---")
        
        st.subheader("Run Quantum Attack Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rsa_preset = st.selectbox(
                "Select RSA Key Preset",
                options=["Small (Demo)", "Medium", "Large"],
                help="Smaller keys are broken faster"
            )
        
        with col2:
            if st.button("🚀 Launch Shor's Algorithm Attack", key="btn_shor_demo"):
                with st.spinner("Attacking RSA key with Shor's Algorithm..."):
                    try:
                        import shor_algo
                        
                        # Run the attack
                        shor_algo.demonstrate_attack()
                        
                        st.success("✓ Attack simulation completed!")
                        st.info("""
                        **Results:**
                        - The algorithm successfully factored the RSA modulus
                        - Original prime factors were recovered
                        - Private key was reconstructed
                        - RSA encryption is BROKEN for this key
                        """)
                        
                    except Exception as e:
                        st.error(f"Error running Shor's algorithm: {e}")
        
        st.markdown("---")
        
        st.subheader("Security Implications")
        
        st.info("""
        **Current Status (Classical Crypto):**
        - RSA-2048 is considered secure against classical computers
        - Estimated 2^116 operations to break
        - Would take thousands of years with current computers
        
        **With Quantum Computers (Shor's Algorithm):**
        - RSA-2048 can be broken in polynomial time: O(n³)
        - On a 20 million qubit quantum computer: breaks in ~8 hours
        - Current quantum computers have ~1000 qubits (not yet powerful enough)
        
        **Recommendations:**
        - Migrate to Post-Quantum Cryptography (NIST has approved algorithms)
        - Use Lattice-based cryptography, Hash-based cryptography, or Code-based cryptography
        - Do not wait for quantum computers to become a practical threat
        """)
    
    # Tab 3: Blockchain Verification
    with tab3:
        st.subheader("🔐 Blockchain Integrity Verification")
        
        if len(grid.blockchain) == 0:
            st.info("No transactions in blockchain yet")
        else:
            st.info(f"Blockchain contains {len(grid.blockchain)} block(s)")
            
            # Verify Chain
            if st.button("🔍 Verify Blockchain Integrity", key="btn_verify_blockchain"):
                with st.spinner("Verifying blockchain integrity..."):
                    is_valid = grid.verify_chain()
                
                if is_valid:
                    st.success("✓ Blockchain is VALID and UNMODIFIED")
                    st.balloons()
                else:
                    st.error("✗ Blockchain has been TAMPERED WITH!")
            
            st.markdown("---")
            
            # Blockchain Details
            st.subheader("Blockchain Structure")
            
            for i, block in enumerate(grid.blockchain):
                with st.expander(f"Block #{i+1} - {block['timestamp']}", expanded=(i == len(grid.blockchain)-1)):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.code(f"""
Transaction ID: {block['transaction_id']}
Previous Hash:  {block['prev_block_hash'][:32]}...
Timestamp:      {block['timestamp']}
                        """, language="text")
                    
                    with col2:
                        st.code(f"""
UID: {block['uid'][:20]}...
FID: {block['fid'][:20]}...
Amount: {block['amount']:.2f}
Dispute: {block['dispute_flag']}
                        """, language="text")
            
            st.markdown("---")
            
            # Tamper Detection Test
            st.subheader("Tamper Detection Test")
            
            st.warning("""
            **This is a demonstration only!**
            This test would modify a block and verify that tampering is detected.
            In production, never modify blockchain data.
            """)
            
            if st.button("Run Tamper Detection Test", key="btn_tamper_test"):
                st.info("Modifying first block's amount...")
                
                original_amount = grid.blockchain[0]["amount"]
                grid.blockchain[0]["amount"] = 99999999
                
                is_valid = grid.verify_chain()
                
                if not is_valid:
                    st.success("✓ Tampering successfully detected!")
                else:
                    st.error("✗ Tampering not detected (unexpected)")
                
                # Restore
                grid.blockchain[0]["amount"] = original_amount
                st.info("Block restored to original state")
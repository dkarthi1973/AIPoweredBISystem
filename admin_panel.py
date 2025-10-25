import streamlit as st
import requests
import pandas as pd

def show_admin_panel(api_base, token):
    """Admin panel for user management"""
    st.header("👥 User Management (Admin Only)")
    
    # Get all users
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{api_base}/admin/users", headers=headers, timeout=10)
        if response.status_code == 200:
            users = response.json()
            
            if users:
                # Display users table
                df_users = pd.DataFrame(users)
                st.dataframe(df_users[['username', 'email', 'full_name', 'role_name', 'created_at']], use_container_width=True)
                
                # User management actions
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔄 Update User Role")
                    with st.form("update_role_form"):
                        update_username = st.selectbox("Select User", [user['username'] for user in users if user['username'] != 'admin'])
                        new_role = st.selectbox("New Role", ["user", "manager", "admin"], format_func=lambda x: x.capitalize())
                        
                        if st.form_submit_button("Update Role"):
                            role_map = {"admin": 1, "manager": 2, "user": 3}
                            update_data = {"role_id": role_map[new_role]}
                            
                            update_response = requests.put(
                                f"{api_base}/admin/users/{update_username}/role",
                                headers=headers,
                                json=update_data,
                                timeout=10
                            )
                            
                            if update_response.status_code == 200:
                                st.success(f"✅ Updated {update_username} to {new_role} role")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to update role: {update_response.json().get('detail', 'Unknown error')}")
                
                with col2:
                    st.subheader("🗑️ Delete User")
                    with st.form("delete_user_form"):
                        delete_username = st.selectbox("Select User to Delete", 
                                                    [user['username'] for user in users if user['username'] not in ['admin', st.session_state.user['username']]])
                        
                        if st.form_submit_button("Delete User", type="secondary"):
                            delete_response = requests.delete(
                                f"{api_base}/admin/users/{delete_username}",
                                headers=headers,
                                timeout=10
                            )
                            
                            if delete_response.status_code == 200:
                                st.success(f"✅ User {delete_username} deleted successfully")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete user: {delete_response.json().get('detail', 'Unknown error')}")
                
                # Create new user
                st.subheader("➕ Create New User")
                with st.form("create_user_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_username = st.text_input("Username")
                        new_email = st.text_input("Email")
                    with col2:
                        new_full_name = st.text_input("Full Name")
                        new_password = st.text_input("Password", type="password")
                        new_role = st.selectbox("Role", ["user", "manager", "admin"], format_func=lambda x: x.capitalize())
                    
                    if st.form_submit_button("Create User"):
                        if new_username and new_email and new_password:
                            role_map = {"admin": 1, "manager": 2, "user": 3}
                            user_data = {
                                "username": new_username,
                                "email": new_email,
                                "password": new_password,
                                "full_name": new_full_name,
                                "role_id": role_map[new_role]
                            }
                            
                            create_response = requests.post(
                                f"{api_base}/admin/users",
                                headers=headers,
                                json=user_data,
                                timeout=10
                            )
                            
                            if create_response.status_code == 200:
                                st.success("✅ User created successfully!")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to create user: {create_response.json().get('detail', 'Unknown error')}")
                        else:
                            st.error("Please fill all required fields")
            else:
                st.info("No users found.")
        else:
            st.error("❌ Failed to fetch users")
            
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Reset password widget
if authentication_status:
    try:
        if authenticator.reset_password(username):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)

# Register user widget
try:
    email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
    if email_of_registered_user:
        st.success('User registered successfully')
except Exception as e:
    st.error(e)

# Forgot password widget
try:
    username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
    if username_of_forgotten_password:
        st.success('New password to be sent securely')
        # The developer should securely transfer the new password to the user.
    elif username_of_forgotten_password == False:
        st.error('Username not found')
except Exception as e:
    st.error(e)

# Forgot username widget
try:
    username_of_forgotten_username, email_of_forgotten_username = authenticator.forgot_username()
    if username_of_forgotten_username:
        st.success('Username to be sent securely')
        # The developer should securely transfer the username to the user.
    elif username_of_forgotten_username == False:
        st.error('Email not found')
except Exception as e:
    st.error(e)

# Update user details widget
if authentication_status:
    try:
        if authenticator.update_user_details(username):
            st.success('Entries updated successfully')
    except Exception as e:
        st.error(e)

# Update the configuration file
with open('../config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)
# Password-Manager
Web App to create/store your passwords. I've integrated the use of TouchID into the authentication workflow, so this password manager will only work for 1 user (the user that can be authenicated by TouchID) and only on Macs
The passwords are encrypted and you have the ability to add/remove passwords as needed.

# Requirements
1. Create the environment file from requirements.txt
2. Create a encryption key using the below and paste it in settings.py
  Fernet.generate_key()
3. You can then start up the application using:
  python manage.py runserver

from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Password

from mechanize import Browser
from cryptography.fernet import Fernet
import favicon

from . import touchid

# Create your views here.
# this is the views file for the main page of our password manager

#initialize fernet object for encryption
fernet = Fernet(settings.KEY)

#here is the scraper for the image of the url
br = Browser()
#ignore websites that don't want us to parse their site
br.set_handle_robots(False)

def home(request):
    if request.method == "POST":
        if "signup-form" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm-password")

            #For when user's passwords dont match
            if password != confirm_password:
                msg = "Please make sure your passwords match!"
                #the messages feature in django allows you to display one time messages
                #we want to display an error message, so we can use the error function in messages
                messages.error(request, msg)

                #Return to the main page
                return HttpResponseRedirect(request.path)
            
            #for when username already exists
            elif User.objects.filter(username=username).exists():
                msg = "Inputed Username already exists"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)

            #for when email already exists
            elif User.objects.filter(email=email).exists():
                msg = "Inputed Email already exists"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                #the authenticate function returns a User object if the credentials match, else None
                if new_user is not None:
                    login(request, new_user)
                    msg = f"Thanks {username}! - you have sucessfully signed up"
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)
        elif "logout" in request.POST:
            if request.user.is_authenticated:
                msg = f"Thanks {request.user.username}! - you have sucessfully logged out"
                logout(request)
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)
        elif "login" in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            touch_id_successful = touchid.authenticate()
            #Touch ID factor authentication
            if not touch_id_successful:
                msg = "Touch ID Verification Incorret! - Please try again"
                messages.error(request, msg)
            elif user is None:
                msg = "Incorrect Username or Password"
                messages.error(request, msg)
            else:
                login(request, user)
                msg = "Sucessfully Logged In!"
                messages.success(request, msg)
            return HttpResponseRedirect(request.path)
        elif "add-password" in request.POST:
            url = request.POST.get("url")
            email = request.POST.get("email")
            password = request.POST.get("password")
            
            #encrypt password
            #we need to encode the text, because the encrypt method only takes encoded text
            encrypted_email = fernet.encrypt(email.encode())
            encrypted_password = fernet.encrypt(password.encode())
            
            #get logo for url
            try:
                br.open(url)
                title = br.title()
            except:
                title = url
            #url of icon of website
            try:
                icon = favicon.get(url)[0].url
            except:
                icon = "https://cdn-icons-png.flaticon.com/128/1006/1006771.png"
            
            #save data in database
            new_password = Password.objects.create(
                user=request.user,
                name=title,
                logo=icon,
                email=encrypted_email.decode(),
                password=encrypted_password.decode(),
            )
            msg = f"Sucessfully saved password for {title}!"
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)
        elif "delete-password" in request.POST:
            if request.user.is_authenticated:
                password_id_to_delete = request.POST.get('password-id')
                msg = f"Sucessfully deleted password for {Password.objects.get(id=password_id_to_delete).name}!"
                Password.objects.get(id=password_id_to_delete).delete()
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)
    #if user is logged in and authenticated, display their passwords
    context = {}
    if request.user.is_authenticated:
        passwords = Password.objects.all().filter(user=request.user)
        for password in passwords:
            password.email = fernet.decrypt(password.email.encode()).decode()
            password.password = fernet.decrypt(password.password.encode()).decode()
        context = {"passwords": passwords,}
    return render(request, "home.html", context)
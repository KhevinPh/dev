from django.shortcuts import render, redirect

from .forms import CreateUserForm, LoginForm, ThoughtForm, UpdateUserForm, UpdateProfileForm

from django.contrib.auth.models import auth

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from .models import Thought, Profile

#Delete user
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control

# Send email on new user
from django.core.mail import send_mail
from django.conf import settings

def homepage(request):
    return render(request, 'journal/index.html')


def register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)

        if form.is_valid():
            current_user = form.save(commit=False)

            form.save()

            #Send email
            send_mail("Welcome to EdenThough", "Congratulation on creating your account", settings.DEFAULT_FROM_EMAIL, [current_user.email])

            profile = Profile.objects.create(user=current_user)

            messages.success(request, "User Created!")

            return redirect('my-login')

    context = {'RegistrationForm': form}
    return render(request, 'journal/register.html', context)



def my_login(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect('dashboard')

    context = {'LoginForm': form}

    return render(request, 'journal/my-login.html', context)


def user_logout(request):
    auth.logout(request)  

    return redirect("")  

@login_required(login_url='my-login')
def dashboard(request):
    profile_pic = Profile.objects.get(user=request.user)

    context = {'profilePic': profile_pic}

    return render(request, 'journal/dashboard.html', context)


@login_required(login_url='my-login')
def create_thought(request):
    form = ThoughtForm()

    if request.method == 'POST':
        form = ThoughtForm(request.POST)

        if form.is_valid():
            thought = form.save(commit=False)
            thought.user = request.user
            thought.save()

            messages.success(request, "Thought Created!")

            return redirect('my-thought')

    context = {'CreateThoughtForm': form}
    return render(request, 'journal/create-thought.html', context)

@login_required(login_url='my-login')
def my_thought(request):

    current_user = request.user.id

    thought = Thought.objects.all().filter(user=current_user)

    context = {'AllThoughts': thought}

    return render(request, 'journal/my-thought.html', context)


@login_required(login_url='my-login')
def update_thought(request, pk):
    try:
        thought = Thought.objects.get(id=pk, user=request.user)
    except:
        return redirect('my-thought')
    form = ThoughtForm(instance=thought)

    if request.method == 'POST':
        form = ThoughtForm(request.POST, instance=thought)

        if form.is_valid():
            form.save()

            messages.success(request, "Thought Updated!")

            return redirect('my-thought')

    context = {'UpdateThought': form}
    return render(request, 'journal/update-thought.html', context)


@login_required(login_url='my-login')
def delete_thought(request, pk):

    try:
        though = Thought.objects.get(id=pk, user=request.user)
    except:
        return redirect('my-thought')
    
    if request.method == 'POST':
        though.delete()

        messages.error(request, "Thought Deleted!")
        return redirect('my-thought')

    return render(request, 'journal/delete-thought.html')




@login_required(login_url='my-login')
def profile_management(request):

    form = UpdateUserForm(instance=request.user)

    profile = Profile.objects.get(user=request.user)

    form_2 = UpdateProfileForm(instance=profile)

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        form_2 = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid() and form_2.is_valid():
            form.save()
            form_2.save()
            return redirect('dashboard')


    context = {'UserUpdateForm': form, 'PorfileUpdateForm': form_2}
    return render(request, 'journal/profile-management.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='my-login')
def delete_account(request):

    if request.method == 'POST':
        deleteUser = User.objects.get(username=request.user)

        deleteUser.delete()

        return redirect('')

    return render(request, 'journal/delete-account.html')
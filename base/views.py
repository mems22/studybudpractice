from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm 

""" VIEWS FOR LOGGING IN, OUT AND REGISTRATION """
def loginPage(request):
    page = 'login'

    #PREVENTS USER FROM RELOGING IN VIA THE URL 
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            email = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        email = authenticate(request, email=email, password=password)

        if email is not None:
            login(request, email)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')    
        
    context={'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()
    context = {'form':form}

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')

    return render (request, 'base/login_register.html',context)
""" VIEWS FOR LOGGING IN, OUT AND REGISTRATION END """





""" MAIN VIEWS """
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
    ) #Allows you to use browse topics so that you can search specific topics
    #Search using topic name OR name OR description

    topics = Topic.objects.all()[0:4] #Objects allow you to access model database
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms, 'topics':topics, 
    'room_count':room_count, 'room_messages':room_messages}

    return render(request, 'base/home.html',context)

def room(request, pk):
    room = Room.objects.get(id=pk) 

    #This basically asks the db to give us all the messages related to a particular room by most recent
    room_messages = room.message_set.all()
    participants = room.participants.all()

    #CREATING MESSAGES IN A ROOM
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id) #prevents reload under POST


    context = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context={'user':user, 'rooms':rooms,
            'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)
""" MAIN VIEWS END """







""" VIEWS FOR CRUD ROOMS """
@login_required(login_url='login') #Redirects User to login page if they try to access this form
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    #IF STATEMENTS CHECK FOR WHEN SOMETHING IS SUBMITED, SAVES FORM DATA TO DATABASE AND REDIRECTS BACK HOME
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            )
        return redirect('home') #keyword from name

    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login') #Redirects User to login page if they try to access this form
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    #STOPS DIFFERENT USERS FROM EDITING EACH OTHERS PAGES
    if request.user != room.host: 
        return HttpResponse("YOU SHALL NOT PASS!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home') 

    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login') #Redirects User to login page if they try to access this form
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    #STOPS DIFFERENT USERS FROM EDITING EACH OTHERS PAGES
    if request.user != room.host: 
        return HttpResponse("YOU SHALL NOT PASS!")

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})
""" VIEWS FOR CRUD ROOMS END """






""" VIEWS FOR CRUD MESSAGES """
@login_required(login_url='login') #Redirects User to login page if they try to access this form
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
 
    if request.user != message.user: 
        return HttpResponse("YOU CANNOT DELETE SUCH A MESSAGE")

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context={'form':form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html',{'room_messages':room_messages})
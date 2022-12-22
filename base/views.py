from django.shortcuts import render, redirect
from .models import Room
from .forms import RoomForm

#Allows you to display info like templates and models on page
# rooms = [
#     {'id':1, 'name': 'Lets learn Python!'},
#     {'id':2, 'name': 'Lets learn Django!'},
#     {'id':3, 'name': 'Lets learn React!'},
# ]
#Outdated way of displaying info on home page, we now use Room.objects to access the model database rather than having to input here

def home(request):
    rooms = Room.objects.all #Objects allow you to access model database
    context = {'rooms':rooms}
    return render(request, 'base/home.html',context)

def room(request, pk):
    room = Room.objects.get(id=pk) 
    context = {'room':room}
    return render(request, 'base/room.html', context)



""" VIEWS FOR CRUD """
def createRoom(request):
    form = RoomForm()

    #IF STATEMENTS CHECK FOR WHEN SOMETHING IS SUBMITED, SAVES FORM DATA TO DATABASE AND REDIRECTS BACK HOME
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home') #keyword from name

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) #Allows it to update form via its ID
        if form.is_valid():
            form.save()
            return redirect('home') 

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})
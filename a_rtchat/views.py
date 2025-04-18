from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import User, ChatGroup
from .forms import *

# Chat view function
@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        other_user = next((member for member in chat_group.members.all() if member != request.user), None)

    if request.headers.get("HX-Request"):  
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid(): 
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            return render(request, 'a_rtchat/partials/chat_message_p.html', {'message': message, 'user': request.user})

    return render(request, 'a_rtchat/chat.html', {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
    })


@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')

    other_user = get_object_or_404(User, username=username)
    
    my_chatrooms = request.user.chat_groups.filter(is_private=True)
    for chatroom in my_chatrooms:
        if other_user in chatroom.members.all():
            return redirect('chatroom', chatroom.group_name)
    chatroom = ChatGroup.objects.create(is_private=True)
    chatroom.members.add(other_user, request.user)

    return redirect('chatroom', chatroom.group_name)


@login_required
def create_groupchat(request):
    form = NewGroupForm()

    if request.method == 'POST':
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin =request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.group_name)
    context = {
        "form":form
    }
    return render(request,'a_rtchat/create_groupchat.html',context)
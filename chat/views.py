from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import login
from .models import Conversation, Profile
from .forms import SignUpForm
@login_required
def home(request):
    users = User.objects.exclude(id=request.user.id).order_by('username')
    return render(request, 'chat/home.html', {'users': users})
@login_required
def room(request, username):
    other = get_object_or_404(User, username=username)
    if other.id == request.user.id:
        return redirect('chat:home')
    conv, _ = Conversation.get_or_create_dm(request.user, other)
    return render(request, 'chat/room.html', {'conversation': conv, 'other': other})
@login_required
def users_status(request):
    now = timezone.now()
    data = []
    for p in Profile.objects.select_related('user'):
        if p.user_id == request.user.id: continue
        online = now - p.last_seen < timezone.timedelta(seconds=60)
        data.append({'username': p.user.username, 'online': online, 'last_seen': timezone.localtime(p.last_seen).strftime('%Y-%m-%d %H:%M:%S')})
    return JsonResponse({'users': data})
@login_required
def heartbeat(request):
    profile = Profile.objects.get(user=request.user)
    profile.last_seen = timezone.now()
    profile.save(update_fields=['last_seen'])
    return JsonResponse({'ok': True})
@login_required
def history(request, conversation_id):
    from .models import Conversation
    conv = get_object_or_404(Conversation, id=conversation_id, users=request.user)
    msgs = conv.messages.select_related('sender').order_by('-id')[:200]
    out = [{
        'id': m.id, 'sender': m.sender.username, 'text': m.text,
        'timestamp': timezone.localtime(m.created_at).strftime('%Y-%m-%d %H:%M:%S')
    } for m in reversed(list(msgs))]
    return JsonResponse({'messages': out})
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat:home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

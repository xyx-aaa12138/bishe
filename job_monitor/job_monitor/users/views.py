from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def register(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            context['error'] = '用户名和密码不能为空。'
        elif len(password) < 6:
            context['error'] = '密码长度至少 6 位。'
        elif password != confirm_password:
            context['error'] = '两次输入的密码不一致。'
        elif User.objects.filter(username=username).exists():
            context['error'] = '该用户名已存在，请更换。'
        else:
            User.objects.create_user(username=username, password=password)
            return redirect('/login/')

        context['username'] = username

    return render(request, 'register.html', context)


def user_login(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/dashboard/')

        context['error'] = '用户名或密码错误。'
        context['username'] = username

    return render(request, 'login.html', context)


@login_required(login_url='/login/')
def user_home(request):
    return render(request, 'my_home.html')


@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect('/login/')
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt    # 取消csrf
from . import forms
from . import models


@csrf_exempt
def admin_view(request):
    if not request.session.get('is_admin', False):
        return redirect('admin_login')
    if request.method == 'GET':
        users = models.User.objects.all()
        return render(request, 'admin.html', {'users': users})
    elif request.method == 'POST':
        username = request.POST.get('username')
        user = models.User.objects.get(username=username)
        user.delete()
        return redirect('admin')

@csrf_exempt
def admin_login(request):
    if request.method == 'GET':
        return render(request, 'admin_login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Replace 'admin' and 'admin_password' with your actual admin username and password
        if username == 'admin' and password == 'admin_password':
            request.session['is_admin'] = True
            return redirect('admin')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid username or password'})
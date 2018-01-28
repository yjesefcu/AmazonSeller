#-*- coding:utf-8 -*-
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext
from rolepermissions.roles import get_user_roles

# Create your views here.


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
            auth.login(request, user)
            # Redirect to a success page.
            response= HttpResponse(json.dumps({'result': 'success'}), content_type='application/json')
            response.set_cookie('my_cookie','cookie value')
            return redirect('/')
        else:
            return render_to_response('login.html', context_instance=RequestContext(request, {'error', u'用户名或密码错误'}))
    else:
        return render_to_response('login.html')


def logout(request):
    auth.logout(request)
    return redirect('login.html')


@login_required
def home(request):
    return render_to_response('index.html', context_instance=RequestContext(request, {'user': request.user}))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import html
import http.cookies
import os
import socket



from threading import Thread
from time import sleep
import sys
import pickle, cgitb, codecs, datetime

from _wall import Wall
from Message import *
wall = Wall()

HOST = '127.0.0.1'
PORT = 11111

cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
session = cookie.get("session")
if session is not None:
    session = session.value
user = wall.find_cookie(session)  # Ищем пользователя по переданной куке

form = cgi.FieldStorage()
action = form.getfirst("action", "")

global login
login=""
sysmess=""

#Классы консольного приложения

def socketStart(m_Socket):
    m_Socket.connect((HOST, PORT))
def socketEnd(m_Socket):
    m_Socket.close()
    
def SendMessage(m_Socket, To, From, Type=Messages.M_TEXT, Data='', password=''):
    socketStart(m_Socket)
    msg=Message(To, From, Type, Data)
    msg.SendData(m_Socket, password)
def ReceiveMessage(m_Socket):
    msg=Message()
    hMsg = msg.ReceiveData(m_Socket)
    socketEnd(m_Socket)
    return hMsg



def LoadTpl(tplName):
    docrootname = 'PATH_TRANSLATED'
    with open(os.environ[docrootname]+'/tpls/'+tplName+'.tpl', 'rt') as f:
        return f.read().replace('{selfurl}', os.environ['SCRIPT_NAME'])





if action == "publish":
    m_To=form.getfirst("m_To", "")
    m_To=html.escape(m_To)
    m_Data = form.getfirst("m_Data", "")
    m_Data = html.escape(m_Data)
    if m_Data and user is not None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            SendMessage(s, m_To, user, Messages.M_TEXT, m_Data)
            hmsg=ReceiveMessage(s)
            if hmsg.m_Type==Messages.M_INACTIVE:
                sysmess="Your message will be delivered as soon as the user connects"
            elif hmsg.m_Type==Messages.M_ABSENT:
                sysmess="The user you want to send a message to is not listed"
            elif hmsg.m_Type==Messages.M_CONFIRM:
                sysmess="The message was delivered successfully"
                wall.addMessage(m_To, user, m_Data)
            else:
                sysmess="Something went wrong"
        
        
  
if action == "login":
    login = form.getfirst("login", "")
    login = html.escape(login)
    login='#B'+login
    password = form.getfirst("password", "")
    password = html.escape(password)
    if wall.find(login, password):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            SendMessage(s, "@SERVER", login, Messages.M_INIT, '', password)
            hmsg=ReceiveMessage(s)
            if hmsg.m_Type==Messages.M_INCORRECT:
                sysmess="Sorry, wrong password"
            elif hmsg.m_Type==Messages.M_ACTIVE:
                sysmess="Sorry, this user is already connected. You cannot run one account on different clients"
            elif hmsg.m_Type==Messages.M_EXIST:
                sysmess="Sorry, this user already exists"
            elif hmsg.m_Type==Messages.M_NOUSER:
                sysmess="Sorry, no such user was found"
            elif hmsg.m_Type==Messages.M_CONFIRM:
                sysmess="You have successfully connected to the server\n"
                cookie = wall.set_cookie(login)
                print('Set-cookie: session={}'.format(cookie))
    else:
       
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            SendMessage(s, "@SERVER", login, Messages.M_CREATE,'', password)
            hmsg=ReceiveMessage(s)
            if hmsg.m_Type==Messages.M_INCORRECT:
                sysmess="Sorry, wrong password"
            elif hmsg.m_Type==Messages.M_ACTIVE:
                sysmess="Sorry, this user is already connected. You cannot run one account on different clients"
            elif hmsg.m_Type==Messages.M_EXIST:
                sysmess="Sorry, this user already exists"
            elif hmsg.m_Type==Messages.M_NOUSER:
                sysmess="Sorry, no such user was found"
            elif hmsg.m_Type==Messages.M_CONFIRM:
                sysmess="You have successfully connected to the server\n"
                wall.register(login, password)
                cookie = wall.set_cookie(login)
                print('Set-cookie: session={}'.format(cookie))
        
   
if action == "getdata":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  
        SendMessage(s, "@SERVER", str(user), Messages.M_GETDATA)
        msg=Message()
        hMsg=msg.ReceiveData(s)
        if (hMsg.m_Type == Messages.M_TEXT):
            wall.addMessage(hMsg.m_To.decode('utf-8'), hMsg.m_From.decode('utf-8'), msg.m_Data.decode('utf-8'))


if user is not None:
    pub = '''
    <form action="/cgi-bin/wall.py">
        <input type="text" name="m_To">
        <textarea name="m_Data"></textarea>
        <input type="hidden" name="action" value="publish">
        <input type="submit" value="Send">
    </form>
    '''
    getdt='''
    <form action="/cgi-bin/wall.py">
        <input type="hidden" name="action" value="getdata"> 
        <input type="submit" value="GetData">
    </form>    
    '''
else:
    pub = ''
    getdt=''
    

print('Content-type: text/html\n')
if user is not None:
    print('Active User:', user, '<br>')
    
else: 
    print('Please, Create account or Login', '<br>')

print(LoadTpl('index').format(posts=wall.MessagesList(user), publish=pub, getdata=getdt))
print(sysmess)
#print(pattern.format(posts=wall.html_list(), publish=pub))
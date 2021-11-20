# _*_ coding:utf-8 _*_
# Filename:ServerUI.py
# Python在线聊天服务器端  
 
import tkinter as Tkinter
import tkinter.font as tkFont
import socket
import threading as thread
import time
import sys  

import inspect

import ctypes
#没用到的线程关闭程序
def _async_raise(tid, exctype):

    """raises the exception, performs cleanup if needed"""

    tid = ctypes.c_long(tid)

    if not inspect.isclass(exctype):

        exctype = type(exctype)

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

    if res == 0:

        raise ValueError("invalid thread id")

    elif res != 1:

        # """if it returns a number greater than one, you're in trouble,

        # and you should call it again with exc=NULL to revert the effect"""

        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)

        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):

    _async_raise(thread.ident, SystemExit)

class ServerUI():  
 
    title = 'Python在线聊天-服务器端V1.0'
    local = '127.0.0.1'
    port = 8808
    #global serverSock;
    serverSock = None
    flag = True  
    flagclose = True
    #建立Socket连接
    serverSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSock.bind((local,port))
    serverSock.listen(9)
    buffer = 1024
    id = 0
    th_list = []
    #初始化类的相关属性，类似于Java的构造方法
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.title(self.title)  
 
        #窗口面板,用4个frame面板布局
        self.frame = [Tkinter.Frame(),Tkinter.Frame(),Tkinter.Frame(),Tkinter.Frame()]  
 
        #显示消息Text右边的滚动条
        self.chatTextScrollBar = Tkinter.Scrollbar(self.frame[0])
        self.chatTextScrollBar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)  
 
        #显示消息Text，并绑定上面的滚动条
        ft = tkFont.Font(family='Fixdsys',size=11)
        self.chatText = Tkinter.Listbox(self.frame[0],width=70,height=18,font=ft)
        self.chatText['yscrollcommand'] = self.chatTextScrollBar.set
        self.chatText.pack(expand=1,fill=Tkinter.BOTH)
        self.chatTextScrollBar['command'] = self.chatText.yview()
        self.frame[0].pack(expand=1,fill=Tkinter.BOTH)  
 
        #标签，分开消息显示Text和消息输入Text
        label = Tkinter.Label(self.frame[1],height=2)
        label.pack(fill=Tkinter.BOTH)
        self.frame[1].pack(expand=1,fill=Tkinter.BOTH)  
 
        #输入消息Text的滚动条
        self.inputTextScrollBar = Tkinter.Scrollbar(self.frame[2])
        self.inputTextScrollBar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)  
 
        #输入消息Text，并与滚动条绑定
        ft = tkFont.Font(family='Fixdsys',size=11)
        self.inputText = Tkinter.Text(self.frame[2],width=70,height=8,font=ft)
        self.inputText['yscrollcommand'] = self.inputTextScrollBar.set
        self.inputText.pack(expand=1,fill=Tkinter.BOTH)
        self.inputTextScrollBar['command'] = self.chatText.yview()
        self.frame[2].pack(expand=1,fill=Tkinter.BOTH)  
 
        #发送消息按钮
        self.sendButton=Tkinter.Button(self.frame[3],text=' 发 送 ',width=10,command=self.sendMessage)
        self.sendButton.pack(expand=1,side=Tkinter.BOTTOM and Tkinter.RIGHT,padx=25,pady=5)  
 
        #关闭按钮
        self.closeButton=Tkinter.Button(self.frame[3],text=' 关 闭 ',width=10,command=self.close)
        self.closeButton.pack(expand=1,side=Tkinter.RIGHT,padx=25,pady=5)
        self.frame[3].pack(expand=1,fill=Tkinter.BOTH)  
 
    #接收消息
    def receiveMessage(self):
        
        #循环接受客户端的连接请求
        while(self.flag):
            
            self.connection,self.address = self.serverSock.accept()
            con = self.connection
            self.flag = True
            self.flagclose = True
            self.id = self.id + 1
            #创建子线程持续接收本次连接客户端的消息并把socket接口放进th_list池子
            t1=thread.Thread(target=self.receive,args=(con,))
            t1.setDaemon(True)
            t1.start()
            self.th_list.append(self.connection)
            
    #接收消息线程
    def receive(self,con):
        id_temp = self.id
        while(self.flagclose):
            #接收客户端发送的消息
            self.cientMsg = con.recv(self.buffer).decode('utf-8')
            if not self.cientMsg:
                continue
            elif self.cientMsg == 'Y':
                self.chatText.insert(Tkinter.END,'服务器端已经与' + str(self.id) + '号客户端建立连接......')
                con.send(b'Y')
                con.send(str(id_temp).encode())
            elif self.cientMsg == 'N':
                self.chatText.insert(Tkinter.END,str(id_temp) + '号客户端已关闭......')
                con.send(b'N')
                self.flagclose = False
            else:
                theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.chatText.insert(Tkinter.END, str(id_temp) + '号客户端 ' + theTime +' 说：\n')
                self.chatText.insert(Tkinter.END, '  ' + self.cientMsg)
                for t in self.th_list:
                    self.sendM(t,id_temp,theTime)
    #发送消息
    #自动转发其他人的消息
    def sendM(self,tn,id,time):
        #得到其他客户端发的消息
        message = '00112233abc' + str(id) +'号客户端' + time + '说：' + self.cientMsg + '黄悦健'
        if self.flag == True:
            #将消息发送到客户端
            tn.send(message.encode())
        else:
            #Socket连接没有建立，提示用户
            self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息')
        
    #服务器发送消息给客户端 
    def sendMessage(self):
        #得到用户在Text中输入的消息
        message = self.inputText.get('1.0',Tkinter.END)
        #格式化当前的时间
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
        self.chatText.insert(Tkinter.END,'  ' + message + '\n')
        if self.flag == True:
            #将消息发送到客户端
            for t in self.th_list:
                t.send(message.encode())
        else:
            #Socket连接没有建立，提示用户
            self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息')
        #清空用户在Text中输入的消息
        self.inputText.delete(0.0,message.__len__()-0.0)    
 
    #关闭消息窗口并退出
    def close(self):
        if(self.flagclose):
            self.connection.send(b'N')
        sys.exit()  
 
    #启动线程接收客户端的连接请求
    def startNewThread(self):
        #启动一个新线程来接收客户端的请求
        #thread.start_new_thread(function,args[,kwargs])函数原型，
        #其中function参数是将要调用的线程函数，args是传递给线程函数的参数，它必须是个元组类型，而kwargs是可选的参数
        #receiveMessage函数不需要参数，就传一个空元组
        self.chatText.insert(Tkinter.END,'服务器已经就绪......')
        t=thread.Thread(target=self.receiveMessage,args=())
        t.setDaemon(True)
        t.start()
 
def main():
    server = ServerUI()
    server.startNewThread()
    server.root.mainloop()  
 
if __name__=='__main__':
    main()

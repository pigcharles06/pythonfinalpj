import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk

from multiprocessing import Pool
from multiprocessing import cpu_count
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import random

from numba import jit
import imageio
import os
import pymysql
import tkinter.messagebox as msg

import time

'--------------------------------------------給參數---------------------------------------------------'

a=1
x0=a/2
y0=a/2
N=200
gamma=0.01
epsilon=10**-7
s=15
psi0=0
k0=0
s0=100

'--------------------------------------------資料庫參數---------------------------------------------------'
conn = pymysql.connect(host='127.0.0.1',user='root',passwd='@Abc987chen',db='python',charset='utf8',port=3307)
cur = conn.cursor()
'--------------------------------------------定義函數及給定零矩陣----------------------------------------'
x=np.zeros(N)
y=np.zeros(N)
I=np.zeros([N,N])
I2=np.zeros([N,N])
nor=np.zeros([N,N])
inv=np.zeros([N,N])
psi=np.zeros([N,N],complex)
point = {}
pointi=0        #沙子總數
dispointi=0     #掉落沙子數量
figi=0          #照片數量
filenames=[]
gifname=[]

'----------------------------------------------帳號登入介面---------------------------------------------------'

def login(master):
    tk.Label(master,text='帳號：').place(x=10,y=10)
    lacc=tk.Entry(master,show=None,font=("Arial", 10),width=15)
    lacc.place(x=50,y=10,height=20)
 
    tk.Label(master,text='密碼：').place(x=10,y=40)
    lpass=tk.Entry(master,show=None,font=("Arial", 10),width=15)
    lpass.place(x=50,y=40,height=20)

    '----------------------------------------------帳號註冊---------------------------------------------------'
    
    def reg():
        def dfuser():
            acc=""
            pwd=""
            acc=str(racc.get())
            pwd=str(rpass.get())
            if acc == "" :
                msg.showerror('Error','帳號不能為空')
            else:
                sql = "SELECT * FROM user WHERE account = '"+ acc + "'"
                cur.execute(sql)
                data = cur.fetchone()
                if not data == None:
                    msg.showerror('Error',"{}帳號已存在".format(acc))
                else:
                    sql_insert = "INSERT INTO user(account,password)VALUES('"+acc+"','"+pwd+"')" 
                    #print(sql_insert)
                    cur.execute(sql_insert)
                    conn.commit() 
                    msg.showerror('Error',"{}已註冊成功".format(acc))

        reg_top=tk.Toplevel(master)
        reg_top.geometry("205x135")
        reg_top.title("註冊")
        tk.Label(reg_top,text="帳號：").place(x=10,y=10)
        racc=tk.Entry(reg_top,show=None,font=("Arial", 10),width=15)
        racc.place(x=50,y=10,height=20)
        tk.Label(reg_top,text="密碼：").place(x=10,y=40)
        rpass=tk.Entry(reg_top,show=None,font=("Arial", 10),width=15)
        rpass.place(x=50,y=40,height=20)
        tk.Button(reg_top,text='送出註冊',command=dfuser).place(x=67 ,y=80)
           

    '----------------------------------------------帳號登入---------------------------------------------------'

    def cert():
        acc=str(lacc.get())
        pwd=int(lacc.get())
        if acc == "":
            msg.showerror('Error',"請輸入帳號")
        else:   
            sql_1="SELECT account,password FROM user WHERE account ='" + acc + "'"
            cur.execute(sql_1)
            data= cur.fetchone()   
            if (data==None):
                msg.showerror('Error',"{}帳號不存在".format(acc))
            else:
                mypwd=data[1]
                if pwd=="":
                    msg.showerror('Error',"請輸入密碼")
                else:
                    if (mypwd != pwd):
                        msg.showerror('Error',"密碼錯誤")
                    else:
                        window.destroy()
                        index()

 
    tk.Button(master,text='註冊',command=reg).place(x=50,y=90)
    tk.Button(master,text='登入',command=cert).place(x=110,y=90)
 
    return master #必須return回去

'----------------------------------------------帳號登入後的主畫面---------------------------------------------------'
def index():
    '----------------------------------------------畫圖設定---------------------------------------------------'
    fig=plt.figure(figsize=(30, 30))
    patch = fig.patch
    patch.set_color("#002B36")
    figrg = np.arange(0,N,1)
    SOM=np.shape(inv)                       #(100,100)
    X=np.arange(SOM[1])                     #0-99的陣列
    Y=np.arange(SOM[0])                     #0-99的陣列
    X1,Y1=np.meshgrid(X, Y)

    '----------------------------------------------GUI tk 介面設定---------------------------------------------------'
    window=ttk.Window(themename="solar")
    window.title('GUI')
    window.geometry('1500x900')
    window.resizable(False, False)

    tk.Label(window,text=" 沙子數量:",font=("Arial", 14)).place(x=1200,y=120)
    e1=tk.Entry(window,show=None,font=("Arial", 16),width=10)
    e1.place(x=1300,y=120,anchor="nw")

    tk.Label(window,text=" 波數:",font=("Arial", 14)).place(x=1200,y=250)
    e2=tk.Entry(window,show=None,font=("Arial", 16),width=10)
    e2.place(x=1300,y=250,anchor="nw")
    sc = tk.Scrollbar(window)
    tk.Label(window,text=" 波數:",font=("Arial", 14)).place(x=1200,y=300)
    l1=tk.Listbox(window,height=1,selectborderwidth=6,yscrollcommand=sc.set)
    l1.place(x=1300,y=300)
    sc.place(x=1458,y=300)
    sc.config(command=l1.yview)
    sc2 = tk.Scrollbar(window)
    tk.Label(window,text=" 波數:",font=("Arial", 14)).place(x=1200,y=350)
    l2=tk.Listbox(window,height=1,selectborderwidth=6,yscrollcommand=sc2.set)
    l2.place(x=1300,y=350)
    sc2.place(x=1458,y=350)
    sc2.config(command=l2.yview)
    tk.Label(window,text=" 板子沙子數量:",font=("Arial", 14)).place(x=1200,y=510)
    text3 = tk.StringVar()
    text3.set(str(pointi-dispointi))
    e3=tk.Label(window,textvariable=text3,font=("Arial", 14)).place(x=1400,y=510)


    tk.Label(window,text=" 掉落沙子數量:",font=("Arial", 14)).place(x=1200,y=560)
    text4 = tk.StringVar()
    text4.set(str(dispointi))
    e4=tk.Label(window,textvariable=text4,font=("Arial", 14)).place(x=1400,y=560)


    '----------------------------------------------函數定義---------------------------------------------------'
    def set_sant():
        global pointi
        
        santnum = 0
        if e1.get()!="":
            santnum = int(e1.get())
        ax1=plt.subplot2grid((20,20),(0,0),colspan=15,rowspan=15)
        
        for i in range(pointi,santnum+pointi):
            pointx = random.randint(1,N-2)
            pointy = random.randint(1,N-2)
            point[i]=[pointx,pointy]
            pointi = pointi+1
        
        for i in range(0,pointi):
            ax1.scatter(point[i][0]+random.uniform(-1.0,1.0),point[i][1]+random.uniform(-1.0,1.0),s=5,c='white')   

        ax1.set_yticks(figrg)
        ax1.set_xticks(figrg)
        ax1.axes.xaxis.set_ticklabels([])
        ax1.axes.yaxis.set_ticklabels([])
        ax1.set_facecolor("black")
        
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()    
        canvas.get_tk_widget().place(x=0, y=0)
        text3.set(str(pointi-dispointi))
        
    def clear_sant():
        global pointi
        pointi=0
        point.clear()
        ax1=plt.subplot2grid((20,20),(0,0),colspan=15,rowspan=15)
        ax1.set_yticks(figrg)
        ax1.set_xticks(figrg)
        ax1.axes.xaxis.set_ticklabels([])
        ax1.axes.yaxis.set_ticklabels([])
        ax1.set_facecolor("black")

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()    
        canvas.get_tk_widget().place(x=0, y=0)

    @jit(nopython=True)
    def func(m,n,x,y):    
        fun=(2/a)*np.cos(m*pi*x/a)*np.cos(n*pi*y/a)
        return fun

    @jit(nopython=True)
    def kmn(m,n):
        k=pi/a*np.sqrt(n**2+m**2)
        return k

    def countplot(k):
        global I2
        global inv
        I=np.zeros([N,N])
        nor=np.zeros([N,N])
        inv=np.zeros([N,N])
        psi=np.zeros([N,N],complex)
        for i in range(N):
            x[i]=a*i/N
            for j in range(N):
                y[j]=a*j/N
                for n in range(s):
                    for m in range(s):
                        psi[i,j]+=func(m,n,x[i],y[j])*func(m,n,x0,y0)/(k**2-kmn(m,n)**2+2*complex(0,1)*gamma*k)
                I[i,j]=abs(psi[i,j])**2 
                I2[i,j]=I[i,j]    
        nor=np.sum(I)
        for i in range(N):
            for j in range(N):
                I[i,j]=I[i,j]/nor
                inv[i,j]=1/(I[i,j]+epsilon)
        
    def plot_contour():
        global I2
        k=float(e2.get())#抓取輸入e的東西
        countplot(k)
        ax2=plt.subplot2grid((20,20),(0,15),colspan=5,rowspan=5)
        ax2.contourf(Y1, X1, inv, 90,cmap='Greys_r')
        ax2.set_yticks(())
        ax2.set_xticks(())

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()    
        canvas.get_tk_widget().place(x=0, y=0)
    def plot_max():
        global I2
        k=float(l1.get(l1.curselection()))#抓取輸入e的東西
        countplot(k)
        ax2=plt.subplot2grid((20,20),(0,15),colspan=5,rowspan=5)
        ax2.contourf(Y1, X1, inv, 90,cmap='Greys_r')
        ax2.set_yticks(())
        ax2.set_xticks(())

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()    
        canvas.get_tk_widget().place(x=0, y=0)
    def plot_min():
        global I2
        k=float(l2.get(l2.curselection()))#抓取輸入e的東西
        countplot(k)
        ax2=plt.subplot2grid((20,20),(0,15),colspan=5,rowspan=5)
        ax2.contourf(Y1, X1, inv, 90,cmap='Greys_r')
        ax2.set_yticks(())
        ax2.set_xticks(())

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()    
        canvas.get_tk_widget().place(x=0, y=0)

    def movesant():
        global pointi
        global I2
        global dispointi
        global figi
        global filenames
        dispointi = 0
        x1=0
        y1=0
        ax1=plt.subplot2grid((20,20),(0,0),colspan=15,rowspan=15)
        for i in range(0,pointi):
            x1=point[i][0]
            y1=point[i][1]
            sant0 = I2[x1,y1]       #原本位置

            if x1>0 and x1<N-1 and y1>0 and y1<N-1:
                sant1 = I2[x1-1,y1+1]
                sant2 = I2[x1,y1+1]
                sant3 = I2[x1+1,y1+1]

                sant4 = I2[x1-1,y1]
                sant5 = I2[x1+1,y1]

                sant6 = I2[x1-1,y1-1]
                sant7 = I2[x1,y1-1]
                sant8 = I2[x1+1,y1-1]
            elif x1==0 and y1==0:
                sant2=I2[x1,y1+1]
                sant3=I2[x1+1,y1+1]
                sant5=I2[x1+1,y1]

                sant1 = I2[x1,y1]
                sant4 = I2[x1,y1]
                sant6 = I2[x1,y1]
                sant7 = I2[x1,y1]
                sant8 = I2[x1,y1]
            elif x1==0 and y1<N-1 and y1>0:
                sant1=I2[x1,y1]
                sant4=I2[x1,y1]
                sant6=I2[x1,y1]

                sant2 = I2[x1,y1+1]
                sant3 = I2[x1+1,y1+1]
                sant5 = I2[x1+1,y1]
                sant7 = I2[x1,y1-1]
                sant8 = I2[x1+1,y1-1]
            elif x1==0 and y1==N-1:
                sant1=I2[x1,y1]
                sant2=I2[x1,y1]
                sant3=I2[x1,y1]
                sant4=I2[x1,y1]
                sant6=I2[x1,y1]

                sant5 = I2[x1+1,y1]
                sant7 = I2[x1,y1-1]
                sant8 = I2[x1+1,y1-1]
            elif x1>0 and x1<N-1 and y1==0:
                sant1 = I2[x1-1,y1+1]
                sant2 = I2[x1,y1+1]
                sant3 = I2[x1+1,y1+1]
                sant4 = I2[x1-1,y1]
                sant5 = I2[x1+1,y1]

                sant6 = I2[x1,y1]
                sant7 = I2[x1,y1]
                sant8 = I2[x1,y1]
            elif x1>0 and x1<N-1 and y1==N-1:
                sant4 = I2[x1-1,y1]
                sant5 = I2[x1+1,y1]
                sant6 = I2[x1-1,y1-1]
                sant7 = I2[x1,y1-1]
                sant8 = I2[x1+1,y1-1]

                sant1 = I2[x1,y1]
                sant2 = I2[x1,y1]
                sant3 = I2[x1,y1]
            elif x1==N-1 and y1==0:
                sant1 = I2[x1-1,y1+1]
                sant2 = I2[x1,y1+1]
                sant4 = I2[x1-1,y1]

                sant3 = I2[x1,y1]
                sant5 = I2[x1,y1]
                sant6 = I2[x1,y1]
                sant7 = I2[x1,y1]
                sant8 = I2[x1,y1]
            elif x1==N-1 and y1>0 and y1<N-1:
                sant1 = I2[x1-1,y1+1]
                sant2 = I2[x1,y1+1]
                sant4 = I2[x1-1,y1]
                sant6 = I2[x1-1,y1-1]
                sant7 = I2[x1,y1-1]

                sant3 = I2[x1,y1]
                sant5 = I2[x1,y1]
                sant8 = I2[x1,y1]
            elif x1==N-1 and y1==N-1:
                sant1 = I2[x1,y1]
                sant2 = I2[x1,y1]
                sant3 = I2[x1,y1]
                sant5 = I2[x1,y1]
                sant8 = I2[x1,y1]

                sant4 = I2[x1-1,y1]
                sant6 = I2[x1-1,y1-1]
                sant7 = I2[x1,y1-1]

            arr = np.array([sant0,sant1,sant2,sant3,sant4,sant5,sant6,sant7,sant8])
            minsant=np.argmin(arr)
            if minsant!=0:
                if minsant==1 and sant0>sant1+0.00005:
                    point[i][0] = x1-1
                    point[i][1] = y1+1
                elif minsant==2 and sant0>sant2+0.00005:
                    point[i][0] = x1
                    point[i][1] = y1+1
                elif minsant==3 and sant0>sant3+0.00005:
                    point[i][0] = x1+1
                    point[i][1] = y1+1
                elif minsant==4 and sant0>sant4+0.00005:
                    point[i][0] = x1-1
                    point[i][1] = y1
                elif minsant==5 and sant0>sant5+0.00005:
                    point[i][0] = x1+1
                    point[i][1] = y1
                elif minsant==6 and sant0>sant6+0.00005:
                    point[i][0] = x1-1
                    point[i][1] = y1-1
                elif minsant==7 and sant0>sant7+0.00005:
                    point[i][0] = x1
                    point[i][1] = y1-1
                elif minsant==8 and sant0>sant8+0.00005:
                    point[i][0] = x1+1
                    point[i][1] = y1-1
        
        for i in range(0,pointi):
            x12 = point[i][0]+random.uniform(-1.5,1.5)
            y12 = point[i][1]+random.uniform(-1.5,1.5)
            if x12>=0 and x12<=N-1 and y12>=0 and y12<=N-1:
                ax1.scatter(x12,y12,s=5,c='white')
            else:
                dispointi = dispointi+1


        ax1.set_yticks(figrg)
        ax1.set_xticks(figrg)
        ax1.axes.xaxis.set_ticklabels([])
        ax1.axes.yaxis.set_ticklabels([])
        ax1.set_facecolor("black")

        figi = figi+1
        filename = f'{figi}.png'
        filenames.append(filename)
        plt.savefig(filename)
        
        

    def gotogif():
        global gifname
        global figi
        global filenames
        for i in range(1,figi+1):
            gifname.append(imageio.imread(str(i)+".png"))
        imageio.mimsave("result.gif", gifname,fps=2)

        for filename in set(filenames):
            os.remove(filename)
        figi=0
        filenames=[]
    def run20():
        start=time.time()
        for i in range(20):
            movesant()
        end = time.time()
        print("並行時間:"+str(end-start))
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()    
        canvas.get_tk_widget().place(x=0, y=0)
        text3.set(str(pointi-dispointi))
        text4.set(str(dispointi))

    def changex():
        global x0
        x0=float(e5.get())

    def changey():
        global y0
        y0=float(e6.get())

    def gotoa():
        global x0
        global y0
        y0=a/2
        x0=a/2
    def countk(k):
        psi0=0
        k0=0
        s0=100
        for n in range(s0):
            for m in range(s0):
                psi0+=func(m,n,x0,y0)**2/(k**2-kmn(m,n)**2+2*complex(0,1)*gamma*k)
        k0 = abs(psi0/(1+3.3*psi0))
        return k0

    def plotk():
        k0 = np.arange(1,50.1,0.1,dtype=float)
        f = countk(k0)
        for i,e in enumerate(f):
            if i==0 or i==len(f)-1:
                continue
            if (e>f[i+1] and e>f[i-1]):
                l1.insert(tk.END,round(k0[i],2))
            elif(e<f[i+1] and e<f[i-1]):
                l2.insert(tk.END,round(k0[i],2))
             
        ax3=plt.subplot2grid((20,20),(15,0),colspan=20,rowspan=3)
        ax3.plot(k0,f)
        ax3.grid(True)
        plt.yscale('log')
        my_x_ticks = np.arange( 0, 51, 1)
        ax3.set_xticks(my_x_ticks)
        plt.tick_params(axis='x',colors='white')
        plt.tick_params(axis='y',colors='white')
        

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()    
        canvas.get_tk_widget().place(x=0, y=0)

    '----------------------------------------------畫布介面設定---------------------------------------------------'

    ax1=plt.subplot2grid((20,20),(0,0),colspan=15,rowspan=15)
    ax1.set_yticks(figrg)
    ax1.set_xticks(figrg)
    ax1.axes.xaxis.set_ticklabels([])
    ax1.axes.yaxis.set_ticklabels([])
    ax1.set_facecolor("black")

    ax2=plt.subplot2grid((20,20),(0,15),colspan=5,rowspan=5)
    ax2.contourf(Y1, X1, inv, 90,cmap='Greys_r')
    ax2.set_yticks(())
    ax2.set_xticks(())
    ax2.set_facecolor("black")

    ax3=plt.subplot2grid((20,20),(15,0),colspan=20,rowspan=3)
    ax3.grid(True)
    plt.yscale('log')
    my_x_ticks = np.arange( 0, 51, 1)
    ax3.set_xticks(my_x_ticks)
    plt.tick_params(axis='x',colors='white')
    plt.tick_params(axis='y',colors='white')

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=0,anchor="nw")
    canvas.get_tk_widget().config(width=1100, height=1050)



    '----------------------------------------------GUI tk 按鈕介面設定---------------------------------------------------'
    b1=tk.Button(window,text="佈置沙子",width=15,height=2,bg = "gray",fg = "purple",command=set_sant)
    b1.place(x=1200,y=200,anchor="nw")
    b2=tk.Button(window,text="清除沙子",width=15,height=2,bg = "gray",fg = "purple",command=clear_sant)
    b2.place(x=1350,y=200,anchor="nw")
    b3=tk.Button(window,text="生成結果圖",width=15,height=2,bg = "gray",fg = "purple",command=plot_contour)
    b3.place(x=1200,y=400,anchor="nw")
    b7=tk.Button(window,text="高峰結果",width=15,height=2,bg = "gray",fg = "purple",command=plot_max)
    b7.place(x=1320,y=400,anchor="nw")
    b7=tk.Button(window,text="低峰結果",width=15,height=2,bg = "gray",fg = "purple",command=plot_min)
    b7.place(x=1320,y=455,anchor="nw")
    b4=tk.Button(window,text="移動沙子",width=15,height=2,bg = "gray",fg = "purple",command=run20)
    b4.place(x=1200,y=455,anchor="nw")
    b4=tk.Button(window,text="生成影片",width=15,height=2,bg = "gray",fg = "purple",command=gotogif)
    b4.place(x=1200,y=785,anchor="nw")
    b4=tk.Button(window,text="震源重置",width=15,height=2,bg = "gray",fg = "purple",command=gotoa)
    b4.place(x=1350,y=785,anchor="nw")
    b5=tk.Button(window,text="更改x軸震源(預設為中心點):",width=24,height=3,bg = "gray",fg = "purple",command=changex)
    b5.place(x=1200,y=600,anchor="nw")
    e5=tk.Entry(window,show=None,font=("Arial", 16),width=5)
    e5.place(x=1400,y=600,anchor="nw")
    b6=tk.Button(window,text="更改y軸震源(預設為中心點):",width=24,height=3,bg = "gray",fg = "purple",command=changey)
    b6.place(x=1200,y=700,anchor="nw")
    e6=tk.Entry(window,show=None,font=("Arial", 16),width=5)
    e6.place(x=1400,y=700,anchor="nw")
    b8=tk.Button(window,text="生成k",width=15,height=2,bg = "gray",fg = "purple",command=plotk)
    b8.place(x=1200,y=840,anchor="nw")
    
'----------------------------------------------帳號登入---------------------------------------------------'
if __name__ == "__main__":
    window=ttk.Window(themename="solar")
    window.title("登入")
    window.geometry("205x135")
    window.resizable(False,False)
    login = login(window)
    try:#捕捉直接關閉頁面
        window.wait_window(window=login)#等待login銷毀 銷毀後才執行下面的
    except:
        pass
    window.mainloop()
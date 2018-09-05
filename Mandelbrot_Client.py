import argparse                         #for command line input arguments
import socket                           #for connecting server/client
import queue                            #for Queuing up the tasks
from threading import Thread            #for multiple threads to servers
import numpy
import re

from random import randint             #for testing queuing 
import time

#define command line inputs
parser = argparse.ArgumentParser()      
parser.add_argument("min_c_re", help="minimum real c")
parser.add_argument("min_c_im", help="minimum imaginary c")
parser.add_argument("max_c_re", help="maximum real c")
parser.add_argument("max_c_im", help= "maxmum imaginary c")
parser.add_argument("max_n", help= "maxmum number of iterations")
parser.add_argument("x", help= "pixel size x")
parser.add_argument("y", help= "pixel size y")
parser.add_argument("divisions", help= "divisions for parallelisation")
parser.add_argument("list_of_servers", help= "list of servers, including port (host:port). Min one server", nargs='+')
args=parser.parse_args()

class sendTask(Thread):
    def __init__(self,address,qin,qout):
        Thread.__init__(self)
        self.address = address
        self.qin=qin
        self.qout=qout
 
    def run(self):

        s=socket.socket()       #create socket for server
        s.connect(self.address)      #connect socket to
        while not self.qin.empty():
                task=self.qin.get()
                print(message)       
                s.send(message.encode())
                data=''             #empty string to append recieved packets to
                while True:
                    packet = s.recv(4096)   #recieve packet from data array
                    if bool(re.search("END",packet.decode())): break
                    if bool(re.search("INCORRECT INPUT",packet.decode())): break
                    data+=packet.decode()     #append packet to data

                time.sleep(secondsToSleep)
                self.qin.task_done()

        s.close()

#Dividing the tasks into strips instead of a grid would make it easier to piece together the final image, as strings would
#not need converting and could simply be appended in the right order.
#But I'm not sure if that would be interpreting the assignment to liberally, as it specifies a 4x4 sub-pictures.           
def Main():
        
        nServers=len(args.list_of_servers)      #number of servers

        #set up queue - input queue and output queu
        qin = queue.Queue(maxsize=0)
        qout = queue.Queue(maxsize=0)
        #for x in range(args.divisions*args.divisions):
        #   #code breaking up tasks goes here.

        #test requests. Queue is stored as tuple identifying the task number, and the request string to be sent to server.
        qin.put((1,'Get/mandelbrot/{-1}{-0.5}{0}{0.5}{10}{5}{5}'))          
        qin.put('Get/mandelbrot/{-0.75}{-0.24}{-0.74}{0.25}{20}{20}{30}')
        
        #Set up threads doing Mandelbrot for each server.
        for i in range(0,nServers):             
                address=args.list_of_servers[i].split(':') #parse address into host and port (this doesn't support ipv6 addresses. problem for some other time)
                address=(address[0],int(address[1]))            #change into tuple for socket
                
                #Each server gets a thread
                sThread = sendTask(address,qin,qout)         #creates thread for server
                sThread.setName('Server nr '+str(i+1))  #names thread
                sThread.start()                         #get it going
        
if __name__ == '__main__':
    Main()

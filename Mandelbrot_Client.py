import argparse                         #for command line input arguments
import socket                           #for connecting server/client
import queue                            #for Queuing up the tasks
from threading import Thread            #for multiple threads to servers
import re
import math

#define command line inputs
parser = argparse.ArgumentParser()      
parser.add_argument("min_c_re", help="minimum real c",type=float)
parser.add_argument("min_c_im", help="minimum imaginary c",type=float)
parser.add_argument("max_c_re", help="maximum real c",type=float)
parser.add_argument("max_c_im", help= "maxmum imaginary c",type=float)
parser.add_argument("max_n", help= "maxmum number of iterations",type=int)
parser.add_argument("x", help= "pixel size x",type=int)
parser.add_argument("y", help= "pixel size y",type=int)
parser.add_argument("divisions", help= "divisions for parallelisation",type=int)
parser.add_argument("list_of_servers", help= "list of servers, including port (host:port). Min one server", nargs='+',type=str)
args=parser.parse_args()
nServers=len(args.list_of_servers)

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
                task = self.qin.get()
                s.send(task[1].encode())
                #print(task[1])
                data = ''             #empty string to append recieved packets to
                while True:
                    packet = s.recv(4096)   #recieve packet from data array
                    if bool(re.search("END",packet.decode())): break
                    if bool(re.search("INCORRECT INPUT",packet.decode())): break
                    data+=packet.decode()     #append packet to data

                self.qin.task_done()
                self.qout.put((task[0],data))
                #print("subfig rows = %d \t subfig columns = %d"%( len(data.split('\n')),len(data.split('\n')[0].split(' ')) )   )

        s.close()

#Dividing the tasks into strips instead of a grid would make it easier to piece together the final image, as strings would
#not need converting and could simply be appended in the right order.
#But I'm not sure if that would be interpreting the assignment to liberally, as the example specifies a 4x4 sub-pictures.
def generateQ(qin,min_c_re,min_c_im,max_c_re,max_c_im,x,y,max_n,divisions):
    if divisions>x or divisions>y:
        print("you can't divide pixels.")
        return 1

    #todo: error handling for case of x or y = 1
    re_step = (max_c_re-min_c_re)/(x-1)
    im_step = (max_c_im-min_c_im)/(y-1)

    xidx = 0 #tracking the pixel index of top left corner through the loops
    yidx = y-1

    for j in range(divisions):               #i and j denote the subfigure indices

        if j<y%divisions:                      #this if statement distributes the remainder (y%divisions) in case the pixels cannot be evenly divided
            height_pix = math.floor(y/divisions)   #height of subfigure in pixels
        else:
            height_pix = math.floor(y/divisions) - 1
            
        for i in range(divisions):           #conventional i/j order reversed to start in top left
            if i<x%divisions:                      #this if statement distributes the remainder (x%divisions) in case the pixels cannot be evenly divided
                width_pix = math.floor(x/divisions)    #width of subfigure in pixels
            else:
                width_pix = math.floor(x/divisions)-1
            
            sub_min_re = min_c_re + xidx * re_step #min_c_re for subfigure
            sub_min_im = min_c_im + (yidx - height_pix) * im_step #min_c_im for subfigure
            sub_max_re = min_c_re + (xidx + width_pix) * re_step #max_c_re for subfigure
            sub_max_im = min_c_im + yidx * im_step #max_c_im for subfigure
            request_str='Get/mandelbrot/{%f}{%f}{%f}{%f}{%d}{%d}{%d}'%(sub_min_re,sub_min_im,sub_max_re,sub_max_im,width_pix+1,height_pix+1,max_n)
            qin.put(((xidx,yidx),request_str))
            #print((xidx,yidx))
            xidx += width_pix +1
        xidx = 0
        yidx -= height_pix +1
        
def Main():
        
    #set up queue - input queue and output queue
    qin = queue.Queue(maxsize=0)
    qout = queue.Queue(maxsize=0)   #I'm honestly a bit hazy on the best way to return a value from a thread. Using a queue seems to work okay.
    generateQ(qin,args.min_c_re,args.min_c_im,args.max_c_re,args.max_c_im,args.x,args.y,args.max_n,args.divisions)    #divide up tasks and populate queue
        
    #Set up threads doing Mandelbrot for each server.
    for i in range(0,nServers):             
                address=args.list_of_servers[i].split(':') #parse address into host and port (this doesn't support ipv6 addresses. problem for some other time)
                address=(address[0],int(address[1]))            #change into tuple for socket
                
                #Each server gets a thread
                sThread = sendTask(address,qin,qout)         #creates thread for server
                sThread.setName('Server nr '+str(i+1))  #names thread
                sThread.start()                         #get it going

    
                    
    #This solution for combining the server outputs is a bit ugly, and it was surprising tricky, although I'm sure there's a cleverer solution somewhere.
    #Unfortunately it scales poorly as the file size increases, sort of defeating the point of sending out the tasks, but, hey, it works.
    #I get get sub-figure string from output queue, feed it in to the full picture array, combine into one string when it's done.
    #then stitch the full image string. This would have been super easy in Matlab.
    full_array = [['0'] * args.x for i in range(args.y)] #initiate
    qin.join()
    #putting outputs into array (nested lists)
    while not qout.empty(): #while there's still unfinished tasks
        sub_pic = qout.get()
        sub_array = sub_pic[1]
        xidx = sub_pic[0][0]
        yidx = sub_pic[0][1]
        sub_array = sub_array.split('\n')
        for i in range(len(sub_array)):
                sub_array[i]=sub_array[i].split(' ')  #sub_array is now a 2d array (nested list)
    
        for j in range(len(sub_array)):      #loop through all numbers in the subarray, place into correct coordinates in full array
            for i in range(len(sub_array[0])):
                full_array[len(full_array)-1-yidx+j][xidx+i] = sub_array[j][i]
            

        
        qout.task_done()           
    #PGM file header 
    pgm_str = "P2\n"
    pgm_str += "#Mandelbrot Set. min_c_re=%.1f,min_c_im=%.1f,max_c_re=%.1f,max_c_im=%.1f x=%d, y=%d, max_n=%d\n"%(args.min_c_re,args.min_c_im,args.max_c_re,args.max_c_im,args.x,args.y,args.max_n)
    pgm_str += "%d %d\n"%(args.x,args.y)
    pgm_str += "255\n"
    for j in range(len(full_array)):
        pgm_str += " ".join(full_array[j])
        if not j==len(full_array)-1: pgm_str+='\n'
                    
    with open("Mandelbrot.pgm", "w") as text_file:
        print(pgm_str, file=text_file)
                        
if __name__ == '__main__':
    Main()

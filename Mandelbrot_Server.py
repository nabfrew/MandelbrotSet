import socket   #for connecting server/client
import re       #for parsing request
import sys

import argparse #for parsing command line inputs
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="listening port (default 5000)", type=int, default=5000)
args = parser.parse_args()
        
print(args.port)

#Calculating the Mandelbrot set has been carefully optimised by cleverer people than me before.
#Here I have used as a reference:
#https://www.ibm.com/developerworks/community/blogs/jfp/entry/How_To_Compute_Mandelbrodt_Set_Quickly?lang=en_us
#Selecting fastest available method of calculating Mandelbrot set,
#based on available modules. Easy to add more implementations with function with prototype:
#def NewImplementation(min_c_re,min_c_im,max_c_re,max_c_im,max_n,x,y) {return madnelbrot_array string}

#try:                            
#   import pyopencl as cl           #this is the fastest method according to reference, (including true (rich man's?) parallelism) . 
#   #insert PyOpenCl method here    #However, installation is complex and I haven't spent time on it.
#except ImportError:
try:                            #Numba just-in-time compiler implementation
    from numba import jit
    @jit
    def MandelValue(c,max_n):
        z = c
        for n in range(max_n):
            if abs(z) > 2:
                return int(round(255*n/max_n))  #keeps it to 0-255 format of PGM
            z = z*z + c
        return 0
    @jit
    def MandelSet(min_c_re,min_c_im,max_c_re,max_c_im,x,y,max_n):
        z_str = ''  #empty string to append values to
        re_step = (max_c_re - min_c_re)/(x-1)   #amount to increment c values by
        im_step = (max_c_im - min_c_im)/(y-1)
        real = min_c_re #starting values for top left corner.
        imaginary = max_c_im
        for j in range(y):          #typical nested loop order convention for i/j is reveresed to start in top left while keeping conventional association with i&x,j&y
            for i in range(x):
                z_str += str(MandelValue(real + 1j*imaginary,max_n))
                print('Re = ' + str(real) + ' Im = ' + str(imaginary) +'\n')
                if i!=x: z_str += ' '
                real += re_step
            if j!=y: z_str += '\n'
            real=min_c_re
            imaginary -= im_step
        return z_str
    print("using numba method\n")
except ImportError:
    print("Consider installing numba module for significantly faster calculation.\n")
    def MandelValue(c,max_n):   #'Naive implementation' - just regular python, identical to numba aside from the @jit compiler instruction. 
        z = c
        for n in range(max_n):
            if abs(z) > 2:
                return int(round(255*n/max_n))  #keeps it to 0-255 format of PGM
            z = z*z + c
        return 0
    def MandelSet(min_c_re,min_c_im,max_c_re,max_c_im,x,y,max_n):
        z_str = ''  #empty string to append values to
        re_step = (max_c_re - min_c_re)/(x-1)
        im_step = (max_c_im - min_c_im)/(y-1)
        real = min_c_re #starting values for top left corner.
        imaginary = max_c_im
        for j in range(y):          #typical nested loop order convention for i/j is reveresed to start in top left while keeping conventional association with i&x,j&y
            for i in range(x):
                z_str += str(MandelValue(real + 1j*imaginary,max_n))
                print('Re = ' + str(real) + ' Im = ' + str(imaginary) +'\n')
                if i!=x: z_str += ' '
                real += re_step
            if j!=y: z_str += '\n'
            real=min_c_re
            imaginary -= im_step
        return z_str
    print("using naive method\n")

#doesn't seem particularly useful to output as PGM with header at this stage, but here's the header you'd put at the top if you wanted to.
#PGM file header 
#PGM_HeaderOut = "P2\n"
#PGM_Header += "#Mandelbrot Set. min_c_re=%.1f,min_c_im=%.1f,max_c_re=%.1f,max_c_im=%.1f x=%d, y=%d, max_n=%d\n"%(min_c_re,min_c_im,max_c_re,max_c_im,x,y,max_n)"
#PGM_Header += "%d %d\n"%(x,y)"
#PGM_Header += "255\n"

def Main():
    host = "0.0.0.0"
    port=args.port
     
    mySocket = socket.socket()  #set up connection
    mySocket.bind((host,port))
    mySocket.listen(1)
    conn, addr = mySocket.accept()

    
    print ("Connection from: " + str(addr))
    while True:
            data = conn.recv(1024).decode()
            if not data:
                    break
            data=re.findall("\{(.*?)\}", data)  #parse request.
            if len(data)is not 7:
                print("incorrect input\n")
                print(data)
                conn.send('INCORRECT INPUT'.encode()) #flag it as a broken thread to the client
                return 1
            min_c_re=float(data[0])     #not strictly necessary to 
            min_c_im=float(data[1])     #create new variable, but makes 
            max_c_re=float(data[2])     #code more intelligable
            max_c_im=float(data[3])
            x=int(data[4])
            y=int(data[5])
            max_n=int(data[6])
            
            print ("from connected  user: " + str(data))         
            
            z_str = MandelSet(min_c_re,min_c_im,max_c_re,max_c_im,x,y,max_n)
            print('\nSending data. zval: '+str(sys.getsizeof(z_str))+' bytes.\n')
            #Sending larger dataset was the big timesuck roadblock for me. I tried a few prepackaged methods of converting numpy
            #arrys that didn't seem to work. Ended up writing a function to convert numpy array to string
            #before realising I could modify the mandelbrot function to outpt str to begin with. 
            #sending over TCP
            conn.send(z_str.encode())
            conn.send('END'.encode())   #marks completion of transmission to client
            #mandelbrot_image(z_val,min_c_re,min_c_im,max_c_re,max_c_im,x,y)
 
    conn.close()
    #mandelbrot_image(zval,min_c_re,min_c_im,max_c_re,max_c_im,x,y)
     
if __name__ == '__main__':
    Main()

"# MandelbrotSet" 
Server and client programs written in python 3.7 for calculating Mandelbrot sets and outputting as PMG files.
The client distributes taks to the server.

Client takes positional command line inputs
1. min_c_re           min real value
2. min_c_im           min imagniary value
3. max_c_re           max real value
4. max_c_im           max imaginary value
5. max_n              number of mandelbrot iterations
5. x                  horizontal pixels
6. y                  vertical pixels
7. divisions          defining the grid to break tasks into.
8. list-of-servers    This can be any number of servers, in the format address:port

Client takes 1 optional command line argument:
port -p port to listen to, defaults to 5000

It is highly reccomended to install numba for faster calculation, but the code will run without it. It is structured so that it attempts the fastest method availible. Alternative methods are easy to add by defining new MandelSet() to the nested try/except part of the server code. Further work could include chosing method by optional command line arguments.

The example output files were generated with the commands:

$python Mandelbrot_Client.py -0.74880 0.163749 -0.745667 0.16551 500 1920 1080 500 localhost:5000 localhost:5001

$python Mandelbrot_Client.py -0.74880 0.163749 -0.745667 0.16551 500 1920 1080 100 localhost:5000 localhost:5001

Known issues/further work: 
- The method of recombining the subfigures into the final image does not scale well and could be improved.
- The program fails if the sub-figure sizes are large, greater than ~50 pixels
- There is an error somewhere in how the pixels are assigned under some circumstances. See the bottom right corner in the example output attached for 500 divisions. Some sub-figures in this case also seem to not come through, leaving gaps showing as black squares in the pictures. 

Unfortunately, I have not been able to find the cause and solve these issues.
The program has only been tested on one computer, testing on a real network is still needed.

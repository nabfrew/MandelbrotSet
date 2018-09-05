"# MandelbrotSet" 
Server and client programs for calculating Mandelbrot sets and outputting as PMG files.
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

Note: As explained over email, the programs are not complete, remaining to be done is the code for dividing up tasks and piecing together the output from the servers. With a little more time I am sure I would have no problem doing this, and may do so at a later time if you like.

# Profiling of the code
# CPU Time and memory usage

# 1 timmers

import time

def my_function():
    a= 5+2
    b= 5+3
    c = a+b
    d = c/b
    return d

def my_function2():
    a= 5+2
    b= 5+3
    c = a+b
    return c/b


if __name__ == '__main__':

    start = time.time()
    my_function()
    finish = time.time()
    print(finish - start)

    start = time.time()
    my_function2()
    finish = time.time()
    print(finish - start)
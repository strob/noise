import numpy

# GAME CONFIG
# video frequency, audio bins, y-offset
LEVELS = [(10,  2),
          (20,  4),
          (50,  10),
          (100, 20),
          (1, 0)]
SPEED  = 10

# SYSTEM CONFIG
SIZE   = (240, 320, 3)     # XXX: Maybe, just maybe, numm should allow
                           #      variable output sizing.
A_RATE = 44100

# GAME STATE
level = 0

vnoises= []                     # random, output-size, noise, by level
voffsets=[]                     # y-offset for each level
vxoffset=0                      # x-offset for current level

afreqs = []                     # frequency of audio band
aamps  = []                     # amplitude of each audio band
aphase = []                     # phase of each audio band

mx = SIZE[0]/2                  # mouse
my = SIZE[1]/2

# GAME INIT
def make_levels():
    "randomly"

    # use global variables as a ``fuck you'' to dogmatic programmers.
    global vnoises, voffsets, afreqs, aamps, aphase

    noisegen= [numpy.random.random_integers(0, 255, (X[0], X[0], 3))
               for X in LEVELS]

    # interpolate generated noise to output resolution
    vnoises = []
    for N in noisegen:
        x_idx = numpy.linspace(0, N.shape[1], SIZE[1], endpoint=False)
        y_idx = numpy.linspace(0, N.shape[0], SIZE[0], endpoint=False)
        y_idx = y_idx.reshape((SIZE[0], 1)) # column vector

        x_idx_floor = numpy.floor(x_idx).astype(int)
        x_idx_ceil  = numpy.ceil(x_idx).astype(int)
        x_idx_ceil[x_idx_ceil==N.shape[1]] = 0 # wrap around
        x_idx_weight= x_idx - x_idx_floor
        y_idx_floor = numpy.floor(y_idx).astype(int)
        y_idx_ceil  = numpy.ceil(y_idx).astype(int)
        y_idx_ceil[y_idx_ceil==N.shape[0]] = 0
        y_idx_weight= y_idx - y_idx_floor

        out = numpy.zeros(SIZE)

        for i in range(3):
            # VOODOO! (a.k.a. fast linear interpolation)
            out[:,:,i] = N[y_idx_floor, x_idx_floor, i]*(1-y_idx_weight)*(1-x_idx_weight) + \
                N[y_idx_floor, x_idx_ceil, i]*(1-y_idx_weight)*(x_idx_weight) + \
                N[y_idx_ceil, x_idx_floor, i]*(y_idx_weight)*(1-x_idx_weight) + \
                N[y_idx_ceil, x_idx_ceil, i]*y_idx_weight*x_idx_weight
        
        vnoises.append(out.clip(0,255).astype(numpy.uint8))


    voffsets= [numpy.random.randint(0, SIZE[0]) for X in LEVELS]
    
    afreqs=   [numpy.random.random_integers(60, 2000, (X[1])) #(27, 6800, (X[1])) 
               for X in LEVELS]
    aamps =   [numpy.random.random(size=X[1]) for X in LEVELS]
    aphase=   [numpy.zeros(X[1]) for X in LEVELS]

make_levels()

def dist():
    "0 is close, 1 is far, sqrt(2) is max."
    return pow(
        pow((mx-vxoffset)/float(SIZE[1]), 
            2) + pow(
            (my-voffsets[level])/float(SIZE[0]),
            2),
        0.5)
    
# GAME

def video_out(a):
    global vxoffset
    int_xoff = int(vxoffset)
    x_idx = range(int_xoff, a.shape[1]) + range(int_xoff)
    y_idx = range(voffsets[level], a.shape[0]) + range(voffsets[level])
    y_idx = numpy.array(y_idx, dtype=int).reshape((SIZE[0], 1))
    vxoffset = (vxoffset + SPEED*dist()) % a.shape[1]

    anti_x_idx = range(mx, a.shape[1]) + range(mx)
    anti_y_idx = range(my, a.shape[0]) + range(my)
    anti_y_idx = numpy.array(anti_y_idx, dtype=int).reshape((SIZE[0], 1))


    bgnoise = numpy.zeros(SIZE)
    for i in range(level, len(LEVELS)-1):
        nxr = numpy.random.randint(0, SIZE[1])
        noise_x_idx = range(nxr, a.shape[1]) + range(nxr)
        nyr = numpy.random.randint(0, SIZE[0])
        noise_y_idx = range(nyr, a.shape[0]) + range(nyr)
        noise_y_idx = numpy.array(noise_y_idx, dtype=int).reshape((SIZE[0], 1))
        
        for c in range(3):
            bgnoise[:,:,c] += vnoises[i][noise_y_idx,noise_x_idx,0]
    bgnoise /= (len(LEVELS)-1-level)


    a[:] = (vnoises[level][y_idx,x_idx].astype(int) - \
                vnoises[level][anti_y_idx,anti_x_idx].astype(int) +\
                bgnoise).clip(0,255)

def audio_out(a):
    phasescale = numpy.pi/numpy.sqrt(2)
    antiphase = numpy.pi + phasescale*dist()

    freqs = afreqs[level]
    phase = aphase[level]

    for i,freq in enumerate(freqs):
        step = 2 * numpy.pi * freq * (len(a) / float(A_RATE))

        sinarr = numpy.linspace(
            phase[i],
            phase[i] + step,
            len(a))
        antisinarr = numpy.linspace(
            phase[i] + antiphase,
            phase[i] + step + antiphase,
            len(a))

        a[:,0] += (pow(2,15)/(len(aamps[level])+1)) * aamps[level][i] * (numpy.sin(sinarr) + numpy.sin(antisinarr))

        phase[i] = phase[i] + step % (2 * numpy.pi)
    a[:,1] = a[:,0]
    
def mouse_in(type, px, py, b):
    global mx, my, level
    mx = int(px*SIZE[1])
    my = int(py*SIZE[0])
    if dist() < 0.01 and level < len(LEVELS)-1:
        level += 1

if __name__=='__main__':
    import numm.run
    numm.run(**globals())

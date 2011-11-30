import numm, numpy

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
    global vnoises, voffsets, afreqs, aamps, aphase, vxoffset

    noisegen= [numpy.random.random_integers(0, 1, (X[0], 3))
               for X in LEVELS]

    # interpolate generated noise to output resolution
    vnoises = []
    for N in noisegen:
        x_idx = numpy.linspace(0, N.shape[0], SIZE[1], endpoint=False).astype(int)
        vnoises.append(N[x_idx])

    voffsets= [numpy.random.randint(0, SIZE[1]) for X in LEVELS]

    vxoffset = numpy.random.randint(0,SIZE[1])
    
    afreqs=   [numpy.random.random_integers(60, 2000, (X[1]))
               for X in LEVELS]
    aamps =   [numpy.random.random(size=X[1]) for X in LEVELS]
    aphase=   [numpy.zeros(X[1]) for X in LEVELS]

make_levels()

def dist():
    "0 is close, 1 is far, sqrt(2) is max."
    return pow(
        pow((mx-vxoffset)/float(SIZE[1]), 2), 0.5)
    
# GAME

def video_out(a):
    global vxoffset
    int_xoff = int(vxoffset)
    x_idx = range(int_xoff, a.shape[1]) + range(int_xoff)
    # motion?
    #vxoffset = (vxoffset + SPEED*dist()) % a.shape[1]

    anti_x_idx = range(mx, a.shape[1]) + range(mx)

    a[:] = abs((vnoises[level][x_idx] - \
        vnoises[level][anti_x_idx])*255).clip(0,255)
    
def audio_out(a):
    phasescale = numpy.pi/numpy.sqrt(2)
    antiphase = numpy.pi + phasescale*dist()

    freqs = afreqs[level]
    phase = aphase[level]

    for i,freq in enumerate(freqs):
        step = 2 * numpy.pi * freq * (len(a) / float(A_RATE))

        arr = (numpy.linspace(
            phase[i],
            phase[i] + step,
            len(a)) % (2*numpy.pi) > numpy.pi).astype(numpy.int)
        antiarr = (numpy.linspace(
            phase[i] + antiphase,
            phase[i] + step + antiphase,
            len(a)) % (2*numpy.pi) > numpy.pi).astype(numpy.int)

        a[:,0] += (pow(2,15)/(len(aamps[level])+1)) * \
            aamps[level][i] * \
            (arr + antiarr)

        phase[i] = phase[i] + step % (2 * numpy.pi)
    a[:,1] = a[:,0]
    
def mouse_in(type, px, py, b):
    global mx, my, level, vxoffset
    mx = int(px*SIZE[1])
    my = int(py*SIZE[0])
    if dist() < 0.01 and level < len(LEVELS)-1:
        level += 1
        vxoffset = numpy.random.randint(0,SIZE[1])
        print 'level up'
        

if __name__=='__main__':
    numm.run(**globals())

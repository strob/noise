CFLAGS = -Wall -Werror -O2 $$(pkg-config --cflags sdl)
LDADD = -lm $$(pkg-config --libs sdl)

all: noise2

clean: .PHONY

.PHONY:
	rm -f noise2

noise2: noise2.cc
	g++ $(CFLAGS) -o noise2 noise2.cc $(LDADD)
	strip -s noise2

# specify all source files here
SRCS = calc.c

# specify targets here (names of executables)
TARG = calc

# specify compiler, flags and libs here
CC = gcc
OPTS = -Wall -O -std=gnu99
OBJS = $(SRCS:.c=.o)
LIBS = -lm # placeholder - not needed for forksort

# 'all' is not really needed
all: $(TARG)

# generates target executable
$(TARG): $(OBJS)
	$(CC) -o $(TARG) $(OBJS) $(LIBS)

# generates all object files from matching c files
%.o: %.c
	$(CC) $(OPTS) -c $< -o $@

# cleans up stuff
clean:
	rm -f $(OBJS) $(TARG)

install:
	cp gold /var/cctf/bin/

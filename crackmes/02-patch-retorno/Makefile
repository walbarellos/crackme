CC = gcc
CFLAGS = -O0 -fno-stack-protector -no-pie -m64

all: challenge

challenge: challenge.c
	$(CC) $(CFLAGS) -o challenge challenge.c

clean:
	rm -f challenge

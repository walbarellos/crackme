CC      = gcc
CFLAGS  = -O0 -g -no-pie -fno-stack-protector -Wall
TARGET  = challenge
SRC     = challenge.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)

.PHONY: all clean

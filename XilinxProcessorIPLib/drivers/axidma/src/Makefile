APP = axidma

AR=ar
LIBSOURCES=*.c
OUTS = *.o
NAME := axidma
MAJOR = 1
MINOR = 1
VERSION = $(MAJOR).$(MINOR)

INCLUDES += -I"./."

all: lib$(NAME).a

lib$(NAME).a: $(OUTS)
	$(AR) -rcs lib$(NAME).a $(LDFLAGS) $(OUTS)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $(LIBSOURCES)

clean:
	rm -rf *.o *.so *.so.* *.a*
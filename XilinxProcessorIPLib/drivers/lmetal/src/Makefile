APP = metalapi

AR=ar
LIBSOURCES=*.c
OUTS = *.o
NAME := metalapi

INCLUDES += -I"./."

all: lib$(NAME).a

lib$(NAME).a: $(OUTS)
	$(AR) -rcs lib$(NAME).a $(LDFLAGS) $(OUTS)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $(LIBSOURCES)

clean:
	rm -rf *.o *.so *.so.* *.a*

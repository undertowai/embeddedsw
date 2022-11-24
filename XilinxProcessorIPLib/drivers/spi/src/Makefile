APP = spi

AR=ar
LIBSOURCES=*.c
OUTS = *.o
NAME := spi

METAL_API_PATH=../../lmetal/src
INCLUDES = -I"./."
INCLUDES += -I"$(METAL_API_PATH)"

all: lib$(NAME).a

lib$(NAME).a: $(OUTS)
	$(AR) -rcs lib$(NAME).a $(LDFLAGS) $(OUTS)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $(LIBSOURCES)

clean:
	rm -rf *.o *.so *.so.* *.a*

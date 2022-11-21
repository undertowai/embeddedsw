APP = spi

AR=ar
LIBSOURCES=*.c
OUTS = *.o
NAME := spi

INCLUDES = -I"../../../../../embeddedsw/lib/bsp/standalone/src/arm/cortexr5/"
INCLUDES += -I"../../../../../embeddedsw/lib/bsp/standalone/src/arm/common/gcc/"
INCLUDES += -I"./."

all: lib$(NAME).a

lib$(NAME).a: $(OUTS)
	$(AR) -rcs lib$(NAME).a $(LDFLAGS) $(OUTS)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $(LIBSOURCES)

clean:
	rm -rf *.o *.so *.so.* *.a*

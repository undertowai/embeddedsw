APP = spi-test
METAL_API_PATH=../../lmetal/src
LIBSOURCES=main.c
OUTS = ./main.o
INCLUDES =  -I"../src/"
INCLUDES += -I"$(METAL_API_PATH)"
BOARD_FLAG =
OBJS = ./main.c

SO_SRCS = ./shared.c
SO_OBJS = ./shared.o
SO_NAME = qspi

$(SO_OBJS): $(SO_SRCS)
	$(CC) $(CFLAGS) -c -fPIC $(SO_SRCS) $(INCLUDES)

so: $(SO_OBJS)
	$(CC) $(LDFLAGS) $(SO_OBJS) -shared -Wl,-soname,lib$(SO_NAME).so -o lib$(SO_NAME).so -lmetal -L ../src -lspi -L $(METAL_API_PATH) -lmetalapi

all:
	make -C $(METAL_API_PATH)
	make -C ../src
	$(CC) ${LDFLAGS} $(INCLUDES) $(OBJS) -o $(OUTS) -lmetal -L ../src -lspi -L $(METAL_API_PATH) -lmetalapi

clean:
	rm -rf $(OUTS) $(SO_OBJS) *.o
	make -C ../src clean
	make -C $(METAL_API_PATH) clean

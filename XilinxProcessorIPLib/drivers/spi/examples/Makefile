APP = spi-test
METAL_API_PATH=../../lmetal/src/
LIBSOURCES=main.c
OUTS = ./main.o
INCLUDES =  -I"../src/"
INCLUDES += -I"$(METAL_API_PATH)"
BOARD_FLAG =
OBJS = ./main.c

all: $(RFDC_OBJS)
	make -C $(METAL_API_PATH)
	make -C ../src
	$(CC) ${LDFLAGS} $(INCLUDES) $(OBJS) $(RFDC_OBJS) -o $(OUTS) -lmetal -L ../src -lspi -L $(METAL_API_PATH) -lmetalapi

clean:
	rm -rf $(OUTS) *.o
	make -C ../src clean
	make -C $(METAL_API_PATH) clean

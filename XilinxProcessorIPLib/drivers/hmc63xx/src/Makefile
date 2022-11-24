METAL_API_PATH=../../lmetal/src
INCLUDES =  -I"./."
INCLUDES += -I"$(METAL_API_PATH)"
BOARD_FLAG =
OBJS = ./main.c

SO_SRCS = ./*.c
SO_OBJS = ./*.o
SO_NAME = hmc

%.o: %.c
	$(CC) $(CFLAGS) -c -fPIC $(SO_SRCS) $(INCLUDES)

all: $(SO_OBJS)
	$(CC) $(LDFLAGS) $(SO_OBJS) -shared -Wl,-soname,lib$(SO_NAME).so -o lib$(SO_NAME).so -lmetal -L $(METAL_API_PATH) -lmetalapi

clean:
	rm -rf $(OUTS) $(SO_OBJS) *.o
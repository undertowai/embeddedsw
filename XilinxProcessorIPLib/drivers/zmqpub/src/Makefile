
CXX=g++
MAKE=make
AXI_GPIO_LIB_PATH=../../axi_gpio/src
AXI_DMA_LIB_PATH=../../axidma/src
METAL_API_PATH=../../lmetal/src
LIB_NAME=zmqpub

SO_CC_SRCS = \
	ddr.c \
	shared.c

SO_CXX_SRCS = \
	zmq.cpp \
	ddr_mng.cpp \
	main.cpp \

SO_DEP = $(SO_CC_SRCS) \
		$(SO_CXX_SRCS) \
		zmq.hpp \
		ddr_mng.hpp \
		main.h

SO_OBJS = \
	ddr.o \
	ddr_mng.o \
	zmq.o \
	main.o \
	shared.o

SO_NAME = $(LIB_NAME)

$(SO_OBJS): $(SO_DEP)
	$(CC) $(CFLAGS) -c -fPIC $(SO_CC_SRCS) $(INCLUDES)
	$(CXX) $(CFLAGS) -c -fPIC $(SO_CXX_SRCS) $(INCLUDES)

all: $(SO_OBJS)
	$(MAKE) -C $(AXI_GPIO_LIB_PATH) static
	$(MAKE) -C $(AXI_DMA_LIB_PATH) static
	$(CC) $(LDFLAGS) $(SO_OBJS) -shared -Wl,-soname,lib$(SO_NAME).so -o lib$(SO_NAME).so \
	-lzmq -L $(AXI_DMA_LIB_PATH) -laxidma -L $(AXI_GPIO_LIB_PATH) -laxi_gpio \
	-lmetal -L $(METAL_API_PATH) -lmetalapi

clean:
	rm -rf *.so *.o
	$(MAKE) -C $(AXI_GPIO_LIB_PATH) clean
	$(MAKE) -C $(AXI_DMA_LIB_PATH) clean
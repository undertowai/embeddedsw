
SO_SRCS =*.c
SO_OBJS =*.o
SO_NAME = $(LIB_NAME)

%.o: %.c
	$(CC) $(CFLAGS) -c -fPIC $(SO_SRCS) $(INCLUDES)

all: $(SO_OBJS)
	$(CC) $(LDFLAGS) $(SO_OBJS) -shared -Wl,-soname,lib$(SO_NAME).so -o lib$(SO_NAME).so -lmetal -L $(METAL_API_PATH) -lmetalapi

.PHONY: static
static: lib$(LIB_NAME).a

lib$(LIB_NAME).a: $(SO_OBJS)
	$(AR) -rcs lib$(LIB_NAME).a $(LDFLAGS) $(SO_OBJS)

clean:
	rm -rf $(OUTS) $(SO_OBJS) *.o
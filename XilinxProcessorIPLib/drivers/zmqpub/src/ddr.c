#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdint.h>

int ddr_read(void **ptr, uint64_t addr, uint32_t size)
{
    int fd = open("/dev/mem", O_SYNC | O_RDWR);


    *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, addr);

    if (*ptr == MAP_FAILED) {
        printf("Can't map memory \r\n");
        return -1;
    }
    return fd;
}

void ddr_read_finish(int fd)
{
    close(fd);
}
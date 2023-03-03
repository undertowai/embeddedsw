#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdint.h>

int ddr_map_start(void)
{
    return open("/dev/mem", O_SYNC | O_RDWR);
}

void *ddr_map(int fd, uint64_t addr, uint32_t size)
{
    void *ptr = mmap(NULL, size, PROT_READ, MAP_PRIVATE, fd, addr);

    if (ptr == MAP_FAILED) {
        printf("Can't map memory \r\n");
        return NULL;
    }
    return ptr;
}

int ddr_unmap(void *ptr, uint64_t len)
{
    return munmap(ptr, len);
}

void ddr_map_finish(int fd)
{
    close(fd);
}
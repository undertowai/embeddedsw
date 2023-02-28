
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#include <metal_api.h>
#include <xstatus.h>

static void dsell_sub_sum(s32 *dst, s16 *dwell, u32 samples_in_unit)
{
    u32 i = 0;
    for (; i < samples_in_unit; i++) {
        dst[i] += dwell[i];
        if ((i > 65512 - 10) && (i < 65512 + 10))
        printf("i=%d: dst=%d, d=%d\r\n", i, dst[i], dwell[i]);
    }
}

static void dsell_sub_avg(s32 *dst, u32 samples_in_unit, u32 integrator_depth)
{
    u32 i = 0;
    for (; i < samples_in_unit; i++) {

        if ((i > 65512 - 10) && (i < 65512 + 10))
            printf("Before avg : i=%d: dst=%d\r\n", i, dst[i]);


        dst[i] = dst[i] / (s32)integrator_depth;

        if ((i > 65512  - 10) && (i < 65512 + 10))
            printf("i=%d: dst=%d\r\n", i, dst[i]);
    }
}

int dwell_avg (s32 *dst, u32 ddr_addr_hi, u32 ddr_addr_lo, u32 dwell_offset, u32 samples_in_unit, u32 integrator_depth)
{
    u64 ddr_addr = (u64)ddr_addr_lo | ((u64)ddr_addr_hi << 32);
    const u32 bytes_per_sample = 2;
    u64 ddr_bytes = (integrator_depth * samples_in_unit + dwell_offset) * bytes_per_sample;
    u32 i;
    s16 *dwell_ptr;

    ddr_bytes = (((ddr_bytes - 1) / _SC_PAGE_SIZE) + 1) * _SC_PAGE_SIZE;

    printf("dwell_avg: ddr_addr=%p, ddr_bytes=%d, dwell_offset=%d, samples_in_unit=%d, integrator_depth=%d\r\n",
        (void *)ddr_addr, ddr_bytes, dwell_offset, samples_in_unit, integrator_depth);

    int fd = open("/dev/mem", O_SYNC);
    unsigned char *ddr_mem = mmap(NULL, ddr_bytes, PROT_READ, MAP_SHARED, fd, ddr_addr);

    if (ddr_mem == MAP_FAILED) {
        printf("Can't map memory \r\n");
        return -1;
    }

    memset(dst, 0, samples_in_unit * sizeof(s32));

    dwell_ptr = (s16 *)ddr_mem;
    dwell_ptr += dwell_offset;
    for (i = 0; i < integrator_depth; i++) {
        dsell_sub_sum(dst, dwell_ptr, samples_in_unit);
        dwell_ptr += samples_in_unit;
    }
    dsell_sub_avg(dst, samples_in_unit, integrator_depth);
    close(fd);
    return 0;
}

int ddr_test(u32 ddr_addr_hi, u32 ddr_addr_lo, u32 size)
{
    u64 ddr_addr = (u64)ddr_addr_lo | ((u64)ddr_addr_hi << 32);
    int fd = open("/dev/mem", O_SYNC | O_RDWR);
    u32 *ddr_mem = (u32 *)mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, ddr_addr);
    u32 words = size/4;
    u32 i = 0;
    u32 error_count = 0;

    printf("ddr_test: addr=%p, size=0x%x\r\n", ddr_addr, size);

    if (ddr_mem == MAP_FAILED) {
        printf("Can't map memory \r\n");
        return -1;
    }

    for (i = 0; i < words; i++) {
        ddr_mem[i] = i;
    }

    for (i = 0; i < words; i++) {
        if (ddr_mem[i] != i) {
            error_count++;
        }
    }

    printf("DDR test finished; errors=%d\r\n", error_count);
    close(fd);
    return error_count;
}


int ddr_zero(u32 ddr_addr_hi, u32 ddr_addr_lo, u32 size)
{
    u64 ddr_addr = (u64)ddr_addr_lo | ((u64)ddr_addr_hi << 32);
    int fd = open("/dev/mem", O_SYNC | O_RDWR);
    u32 *ddr_mem = (u32 *)mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, ddr_addr);
    u32 words = size/4;
    u32 i = 0;

    printf("ddr_zero: addr=%p, size=0x%x\r\n", ddr_addr, size);

    if (ddr_mem == MAP_FAILED) {
        printf("Can't map memory \r\n");
        return -1;
    }

    for (i = 0; i < words; i++) {
        ddr_mem[i] = 0;
    }

    close(fd);
    return 0;
}
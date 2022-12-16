
#include <metal/device.h>

#include <dirent.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>

#include <metal/sys.h>
#include <metal/irq.h>
#include <metal/sleep.h>
#include "metal/alloc.h"
#include <metal/device.h>
#include <metal/io.h>

#include "metal_api.h"
#include "xstatus.h"

int _metal_init (void)
{
    struct metal_init_params init_param = {
	    .log_handler	= metal_default_log_handler,
	    .log_level		= METAL_LOG_WARNING,
    };

	if (metal_init(&init_param)) {
		printf("ERROR: Failed to run metal initialization\n");
		return XST_FAILURE;
	}
    return XST_SUCCESS;
}

int metal_dev_io_init(metal_dev_io_t *mdev, const char *devName)
{
    int Status = XST_SUCCESS;

 	if (_metal_init() != XST_SUCCESS) {
		return XST_FAILURE;
	}   

    Status = metal_device_open_wrap("platform", devName, &mdev->device);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", devName);
		return XST_FAILURE;
	}

	mdev->io = metal_device_io_region(mdev->device, 0);

	if (NULL == mdev->io) {
        metal_device_close(mdev->device);
		return XST_FAILURE;
	}

    return Status;
}

void Xil_AssertNonvoid(int Expression)
{
	if (!Expression) {
		abort();
	}
}

void Xil_AssertVoid(int Expression)
{
	Xil_AssertNonvoid(Expression);
}

void Xil_AssertNonvoidAlways()
{
	Xil_AssertNonvoid(FALSE);
}

void Xil_AssertVoidAlways()
{
	Xil_AssertNonvoid(FALSE);
}

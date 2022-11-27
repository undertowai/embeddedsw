
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

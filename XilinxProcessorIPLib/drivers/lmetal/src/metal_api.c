
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

s32 X_GetDevice(Xmetal_dev_parm_t *parm)
{
	s32 Status = -1;
	u32 Data = 0;
	char CompatibleString[NAME_MAX];
	char DeviceName[NAME_MAX];
	struct metal_device *DevicePtr;
	DIR *DirPtr;
	struct dirent *DirentPtr;
	char Len = strlen(parm->compatible);
	char NameLen = strlen(parm->name);

	DirPtr = opendir(parm->platform_dir);
	if (DirPtr) {
		while ((DirentPtr = readdir(DirPtr)) != NULL) {

			if (strncmp(DirentPtr->d_name, parm->name, NameLen) == 0) {
				Status = metal_device_open("platform", DirentPtr->d_name, &DevicePtr);
				if (Status) {
					metal_log(METAL_LOG_ERROR, "\n Failed to open device %s", DirentPtr->d_name);
					continue;
				}

				Status = metal_linux_get_device_property(DevicePtr, parm->property,
									 CompatibleString, Len);

				if (Status < 0) {
					metal_log(METAL_LOG_ERROR, "\n Failed to read device tree property");
				} else if (strncmp(CompatibleString, parm->compatible, Len) == 0) {
					Status = 0;
					metal_device_close(DevicePtr);
					break;
				}
				metal_device_close(DevicePtr);
			}
		}
	}

   Status = (s32)closedir(DirPtr);
   if (Status < 0) {
      metal_log(METAL_LOG_ERROR, "\n Failed to close directory");
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

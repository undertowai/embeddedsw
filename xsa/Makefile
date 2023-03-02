
FPGA_BITS = design_1_wrapper.bin
FPGA_BITS_UPD_FLAG=/tmp/$(FPGA_BITS).upd
RM=rm
TOUCH=touch

$(FPGA_BITS_UPD_FLAG): $(FPGA_BITS)
	@ ./fpga.sh $(FPGA_BITS)
	@ $(TOUCH) $(FPGA_BITS_UPD_FLAG)

all: $(FPGA_BITS_UPD_FLAG)

clean:
	$(RM) $(FPGA_BITS_UPD_FLAG)
# Makefile
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/router.sv

TOPLEVEL = router
MODULE = verify_noc

include $(shell cocotb-config --makefiles)/Makefile.sim

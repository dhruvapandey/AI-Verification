# Makefile (Save this INSIDE the 'run' folder)

# Simulator setup
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# 1. Point to the Verilog file in the parent directory (../)
VERILOG_SOURCES += $(PWD)/../router.sv

# Python module settings
TOPLEVEL = router
MODULE = verify_noc

# 2. Tell Python to look for scripts in the parent directory
export PYTHONPATH := $(PWD)/..:$(PYTHONPATH)

# Standard Cocotb include
include $(shell cocotb-config --makefiles)/Makefile.sim

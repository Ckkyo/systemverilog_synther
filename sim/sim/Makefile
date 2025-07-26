SIM ?= vcs# default sim

PRJ_DIR = $(shell pwd)/..
FILE_LIST_PATH ?= ${PRJ_DIR}/sim/filelist.f
SV_LOG_FILE_PATH ?= ./log
FILE_LIST_DIR ?= ${PRJ_DIR}/sim/

WORK_DIR ?= ~/sva_synth_sim_work
TEST_CASE ?= test21

create_work:
	mkdir -p ${WORK_DIR}

##################
XRUN_TCL_PATH := ${PRJ_DIR}/sim/run.tcl  ## xrun tcl patch

OPTION_XRUN := -64bit -sv -notimingcheck -access +rwc -accessreg +rwc \
				-uvmaccess -date -dumpstack -negdelay -timescale 1ns/1ns \
				-lwdgen -f $(FILE_LIST_PATH) +SV_LOG_FILE_PATH=${SV_LOG_FILE_PATH} \
				-input $(XRUN_TCL_PATH) -l xrun.log 

OPTION_VCS := -f $(FILE_LIST_PATH)	\
	-timescale=1ns/1ps	\
	+define+DUMP	+SV_LOG_FILE_PATH=${SV_LOG_FILE_PATH} \
	-debug_access -R -full64 +vc +v2k -sverilog -debug_acc+all	\
	-debug_region+cell+encrypt	\
	-P ${LD_LIBRARY_PATH}/novas.tab  ${LD_LIBRARY_PATH}/pli.a

OPTION_Verdi := -f $(FILE_LIST_PATH) -ssf *.fsdb &
################


OPTION_COMMON += -top tb
SIM_ENV = PRJ_DIR=${PRJ_DIR} FILE_LIST_DIR=${FILE_LIST_DIR}
################

sim_xrun :create_work
	@echo ${PRJ_DIR}
	@echo "Welcome!"
	@echo "SIM is $(SIM) and dubug support indago" 
	cd ${WORK_DIR} && ${SIM_ENV} xrun  $(OPTION_XRUN) ${OPTION_COMMON} +define+${TEST_CASE} || echo "sim done"

sim_vcs :create_work
	@echo SV_LOG_FILE_PATH=${SV_LOG_FILE_PATH}
	@echo "SIM is $(SIM) and dubug support verdi"
	@cd ${WORK_DIR} && ${SIM_ENV} vcs $(OPTION_VCS) +define+${TEST_CASE} || echo "sim done" 


	
	
# @cd ${WORK_DIR} && rm -rf xcelium.d/run.d && cp -a xcelium.d/run.lnx8664.20.09.d xcelium.d/run.d 


indago :
	@echo "Debug is indago"
	@cd ${WORK_DIR} && indago
	@echo "Welcom indago !"

log :
	@cp ${WORK_DIR}/xrun.log ./xrun.log

verdi	:
	@echo "Debug is verdi"
	@cd ${WORK_DIR} && verdi $(OPTION_Verdi)
	@echo "Welcom verdi !"

clean:
	rm -rf ${WORK_DIR}/* ${WORK_DIR}.* ./xrun.log ../log ${WORK_DIR}/*

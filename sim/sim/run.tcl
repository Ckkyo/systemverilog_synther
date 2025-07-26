ida_database -open -name="ida.db"
ida_probe -log -sv_flow -uvm_reg -log_objects -sv_modules -wave -wave_probe_args= "tb -depth all -all -memories -variables -packed 10000000 -unpacked 10000000 -dynamic" -wave_glitch_recording
run
exit

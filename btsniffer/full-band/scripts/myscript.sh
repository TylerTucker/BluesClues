#!/bin/bash
rm ../outputtrace*
timeout 15s ../ismsniffer/build/ismsniffermt --runlo --lorxgain 70 --loargs "serial=31C9C2A" --runhi --hirxgain 70 --hiargs "serial=327533B" --txgain 70
EXECPATH="../sources/synch-processing"
$EXECPATH/bledecoder ../usrp_samples_lo.dat ../usrp_samples_hi.dat | ../scripts/processsynch.pl > ../synchtimetrace.txt
timeout 10s ./processtrace.sh
#!/bin/sh

#Script za assign IRQ kum CPU thread ;) by XaMaB

if [ $# -lt 2 ]; then
	echo
	echo usage: [NIC]  [CPU CORE RANGE]
	echo example:	$0 eth2		0-15
	echo
	exit 1
fi

DEV=$1
CPU_N=$2


IRQ_N=$(grep ${DEV} /proc/interrupts |awk 'NR > 1 { print prev } { prev = $0 }'|cut -d':' -f1)
SEQ=$(echo $CPU_N | sed 's/-/ /')
CPULIST=$(seq -s , $SEQ )

I=1
for IRQ in $IRQ_N
do
    core_id=$(echo $CPULIST | cut -d',' -f${I})
    echo Assign irq $IRQ mask 0x$(printf "%x" $((2**core_id)))
    bit_mask=$(printf "%x" $((2**core_id))| rev | sed 's/.\{8\}/&,/g ; s/,$//g;' | rev )
    echo $bit_mask > /proc/irq/$IRQ/smp_affinity
    I=$(($I + 1))
done






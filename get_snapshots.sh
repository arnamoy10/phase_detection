#!/bin/bash

#remove the previous files
rm -f previous_traces current_traces snapshots bash_script_id stage_output

#run the python script in background
python3 get_thread_traces.py &

pid=`pidof java`
self_pid=$$
echo $self_pid > bash_script_id

received=0

trap "received=1" SIGINT SIGTERM


#echo $pid
while true;do
	#get five snapshots
	echo Collecting the snapshots
	count="0"
	while [  $count -lt 5 ]; do
		#echo count is $count
		jstack $pid >> snapshots
		count=$[$count+1]
		sleep 5
	done

	echo Processing the snapshots
	#sleep 3
	cat snapshots | java -jar jtda-cli.jar > current_traces
	#remove the hex addresses, because they will change from time to
	#time
	sed -i 's/<0x[0-9a-zA-Z]*>//g' current_traces
	rm -f snapshots
	
	#check if previous_traces exists
	if [ ! -f previous_traces ]; then
		mv current_traces previous_traces
	else
		#do the python analysis
		echo Signalling the python script
		pid_python=`ps aux|grep 'get_thread_traces.py'|grep -v grep|awk '{print $2}'`
		kill -2 $pid_python
		#TODO perform a back and forth talking
		while [ $received -eq 0 ];do
			a=1
		done
		mv current_traces previous_traces
		received=0
	fi
done

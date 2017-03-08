import os, sys
import signal

stage_names=set()
output=open("stage_output","a+")

def get_stages():
	global stage_names
	with open("stage_names") as f:
		content = f.readlines()
	stage_names=set(content)

def update_stages(stack_trace):
	global stage_names
	f = open("stage_names","a")
	f.write(stack_trace+"\n")

def get_trace(file_name):
	set_content = set()
	with open(file_name) as f:
		content = f.readlines()
	start = 0
	string =""
	for line in content:
		#if line contains "stack", new stack
		if "Stack:" in line:
			#print ("found stack start")
			start = 1
		if(start == 1):
			#print ("found stack start")
			string=string+line.rstrip('\n')
			#find the last line of the trace
			if not line.rstrip('\n'):
				#print ("found stack end")
				#print(string)
				start = 0
				set_content.add(string)
				string = ""

	return set_content


def stage_detection(signal, frame):

	current_content=get_trace("current_traces")
	previous_content=get_trace("previous_traces")

	with open("bash_script_id") as f:
		script_id = f.readline().rstrip('\n')
	command="kill -2 "+script_id
	diff=current_content.symmetric_difference(previous_content)
	if(bool(diff)):
		#print("Found new stage")
		#see if present in the previous stage library
		stage_name=""
		#TODO: do you need prev_stage->current_stage or just
		#current_stage is fine to define a stage
		#for x in sorted(previous_content):
		#	stage_name = stage_name+x.rstrip('\n')
		#stage_name = stage_name + "-->"
		for x in sorted(current_content):
			stage_name = stage_name+x.rstrip('\n')

		#stage_found = 0
		#with open("stage_names") as f1:
		#	for line in f1:
		#		if (stage_name in line.rstrip('\n')):
		#			stage_found = 1
		#			break

		if(stage_name not in stage_names):
			#new stage
			#print("Found new stage\n")
			output.write("Found new stage\n")
			sys.stdout.flush()
			#f = open("stage_names","a")
			#f.write(stage_name+"\n")
			stage_names.add(stage_name)
		else:
			#print("***stage change with previous stage***\n")
			output.write("***stage change with previous stage***\n")
			sys.stdout.flush()
	os.system(command)
signal.signal(signal.SIGINT, stage_detection)
while True:
	i = 1

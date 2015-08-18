#script

import subprocess
import time
import sys
import os.path
import re

def get_n_configservers():
	'''returns the number of configservers as passed by the user'''
	return sys.argv[3]
	
def download_build():
	'''replaces the devsource with the ip and then downloads the build using wget command'''
	log_string = "Changing the current working directory to /home/ubuntu"
	#os.fchdir("/home/ubuntu")
	build_link = "http://devsource/lcloud/builds/cloud-5.4.1r30506.tar.gz"
	build_link = build_link.replace("devsource","192.168.33.2")
	shell_command = "wget "+build_link
	child = subprocess.Popen(shell_command, shell=True,stdout=subprocess.PIPE)
	(stdout, stderrdata) = child.communicate()
	stdout_list = list(stdout)
	line = ""
	my_lines = []
	for item in stdout_list:
		line = line + item
		if item == "\n":
			my_lines.append(line)
			line = ""
	for each_line in my_lines:
		print_log("DEBUG",each_line)
	
	log_string = "Build downloaded successfully to /home/ubuntu"
	
def extract_build():
	'''executes the existing extract.sh script to upgrade the cloud'''
	log_string = "Changing the current working directory to /home/ubuntu"
	os.fchdir("/home/ubuntu")
	
def exec_command():
	'''Shows the output of the ps -ef command on the screen'''
	log_string = "After running ps -ef | grep python command:"
	print_log("DEBUG",log_string)
	shell_command = "ps -ef | grep python"
	child = subprocess.Popen(shell_command, shell=True,stdout=subprocess.PIPE)
	(stdout, stderrdata) = child.communicate()
	stdout_list = list(stdout)
	line = ""
	my_lines = []
	for item in stdout_list:
		line = line + item
		if item == "\n":
			my_lines.append(line)
			line = ""
	for each_line in my_lines:
		print_log("DEBUG",each_line)
	
def get_ports_syncservers():
	''' reads the haproxy.cfg file and returns the list of ports on which
	the syncserver process should run and if the file is not presend then it 
	returns the empty list'''
	is_file = os.path.isfile("/etc/haproxy/haproxy.cfg")
	port_list = []
	
	if is_file:
		log_string = "haproxy.cfg file is present\nReading the number of ports from haproxy.cfg"
		print_log(log_string)
		with open("/etc/haproxy/haproxy.cfg","r") as myfile:
			file_lines = myfile.readlines()
		
		for each_line in file_lines:
			pattern = "sync"+"(.*?)"+":"+"(\d+)"
			SP = re.search(pattern, each_line)
			
			if SP:
				port_list.append(SP.group(2))
		log_string = "Total"+len(set(port_list))+"ports:"+set(port_list)
		print_log(log_string)
		return port_list
	else:
		log_string = "haproxy.cfg file is not present,only 1 syncserver process should run"
		print_log(log_string)
		return port_list

def get_config_srv_status(n):
	'''returns true if all the configserver processes are started successfully, 
	false otherise'''
	n = int(n)
	shell_command = "ps -ef | grep inSyncConfigServer.py"
	child = subprocess.Popen(shell_command, shell=True,stdout=subprocess.PIPE)
	(stdout, stderrdata) = child.communicate()
	stdout_list = list(stdout)
	line = ""
	my_lines = []
	for item in stdout_list:
		line = line + item
		if item == "\n":
			my_lines.append(line)
			line = ""
	count = 0
	for i in range(1,n+1):
		for each_line in my_lines:
			pattern = "inSyncConfigServer.py -y -c "+str(i)
			SP = re.search(pattern,each_line)
			if SP:
				count +=1
				break
	if count == n:
		return True
	else:
		return False

def get_sync_srv_status():
	'''returns true if all the syncserver processes are started successfully, 
	false otherise'''
	shell_command = "ps -ef | grep -i syncserver"
	child = subprocess.Popen(shell_command, shell=True,stdout=subprocess.PIPE)
	(stdout, stderrdata) = child.communicate()
	stdout_list = list(stdout)
	line = ""
	my_lines = []
	for item in stdout_list:
		line = line + item
		if item == "\n":
			my_lines.append(line)
			line = ""
	count = 0
	port_list = get_ports_syncservers()
	log_string = "List of ports from haproxy.cfg:",port_list
	port_list = set(port_list)
	for each_port in port_list:
		for each_line in my_lines:
			pattern = "python inSyncSyncServer.py -d -y -p "+str(each_port)
			print "pattern to search:", pattern
			SP = re.search(pattern,each_line)
			if SP:
				count +=1
				break
	if count == len(port_list):
		return True
	else:
		return False		
		
def get_srv_stop_status(service):
	'''checks if the given service is stopped or not, returns True if the 
	service is stopped and False otherwise. ps -ef command is used for this'''
	shell_command = "ps -ef | grep "+"\""+service+".py"+"\""
	child = subprocess.Popen(shell_command, shell=True,stdout=subprocess.PIPE)
	(stdout, stderrdata) = child.communicate()
	stdout_list = list(stdout)
	line = ""
	my_lines = []
	for item in stdout_list:
		line = line + item
		if item == "\n":
			my_lines.append(line)
			line = ""
	for each_line in my_lines:
		pattern = str(service)
		SP = re.search(pattern,each_line)
		if SP:
			SP_ = re.search("python",each_line)
			if SP_:
				return False
	return True
	
def print_log(status,log_string):
	'''function to pring the required log string and send it to STDOUT'''
	c_time = time.ctime()
	log_string = "["+c_time+"]"+"["+status+"]"+" "+log_string
	print log_string
	with open("/upgrade_cloud.log","a") as myfile:
		myfile.write(log_string+"\n")
	
def format_srv_name(service):
	return ("["+service+"]")
	
def stop_cloud():
	'''stop the cloud services:inSyncConfigServer,inSyncSyncServer,inSyncCPortal,
	and SPortal'''
	service_list = ["SPortal","CPortal","ConfigServerSpawner","ConfigServer","SyncServer"]
	for service in service_list:
		log_string = "Checking status of"+format_srv_name(service)+"service"
		print_log("INFO",log_string)
		status = get_srv_stop_status(service)
		if status:
			log_string =  format_srv_name(service)+"service not running, no need to stop"
			print_log("INFO",log_string)
		else:
			log_string = format_srv_name(service)+"service is running"
			print_log("INFO",log_string)
			shell_command = "sudo service "+service+" stop"
			subprocess.check_call(shell_command, shell=True)
			log_string = "Validating status of"+format_srv_name(service)+"service"
			print_log("INFO",log_string)
			status = get_srv_stop_status(service)
			if status:
				log_string = format_srv_name(service)+"service successfully stopped."
				print_log("INFO",log_string)
			while status == False:
				log_string = "Waiting for 10 seconds for"+format_srv_name(service)+"to stop"
				print_log("INFO",log_string)
				time.sleep(10)
				status = get_srv_stop_status(service)
				if status:
					log_string = format_srv_name(service)+"service successfully stopped."
					print_log("INFO",log_string)
					break
	log_string = "All cloud sevices successfully stopped,sleeping for 5 seconds"
	print_log("INFO",log_string)
	time.sleep(5)
	
def stop_nodemaster():
	log_string = "Stopping NodeMaster services:"
	print_log("INFO",log_string)
	shell_command = " sudo dr-stopservice NodeMaster"
	subprocess.check_call(shell_command, shell=True)
	log_string = "Services for all nodemaster successfully stopped, sleeping for 5 seconds"
	time.sleep(5)
	print_log("INFO",log_string)
	
	
def start_nodemaster():
	'''starts the nodemaster sevices'''
	log_string = "Starting NodeMaster services:"
	print_log("INFO",log_string)
	shell_command = " sudo dr-startservice NodeMaster"
	subprocess.check_call(shell_command, shell=True)
	log_string = "Services for all nodemaster successfully started, sleeping for 5 seconds"
	print_log("INFO",log_string)
	time.sleep(5)

def start_cloud():
	'''starts all the cloud master services one by one, waits if the service is not 
	getting started'''
	service_list = ["ConfigServerSpawner","SyncServer","CPortal","SPortal"]
	log_string = "Starting CloudMaster services:"		
	print_log("INFO",log_string)
	for service in service_list:
		subprocess.check_call(shell_command, shell=True)
		if service == "ConfigServerSpawner":
			shell_command = " sudo service [ConfigServerSpawner] start"
			log_string = "Validating the status of [ConfigServer] process"
			status = get_config_srv_status("2")
			while status == False:
				status = get_config_srv_status("2")
				if status:
					log_string = "All [ConfigServer] processes started successfully"
					print_log("INFO",log_string)
					break
				else:
					log_string = "Not all [ConfigServer] started, waiting for 10 seconds..."
					print_log("INFO",log_string)
					time.sleep(10)
		elif service == "SyncServer":
			log_string = "Validating the status of [SyncServer] process"
			status = get_config_srv_status("2")
			while status == False:
				status = get_config_srv_status("2")
				if status:
					log_string = "All [SyncServer] processes started successfully"
					print_log("INFO",log_string)
					break
				else:
					log_string = "Not all [SyncServer] processes started, waiting for 10 seconds..."
					print_log("INFO",log_string)
					time.sleep(10)
		else:
			shell_command = "sudo service "+service+" start"
			subprocess.check_call(shell_command, shell=True)
			log_string = "Validating status of"+format_srv_name(service)+"service"
			print_log("INFO",log_string)
			status = get_srv_stop_status(service)
			if not status:
				log_string = format_srv_name(service)+"service successfully started."
				print_log("INFO",log_string)
			while status == True:
				log_string = "Waiting for 10 seconds for"+format_srv_name(service)+"to start"
				print_log("INFO",log_string)
				time.sleep(10)
				status = get_srv_stop_status(service)
				if not status:
					log_string = format_srv_name(service)+"service successfully stopped."
					print_log("INFO",log_string)
					break
					
	log_string = "All cloud sevices successfully started,sleeping for 5 seconds"
	print_log("INFO",log_string)
	time.sleep(5)
	
if __name__ == "__main__":
	#stop_cloud()
	#exec_command()
	#stop_nodemaster()
	download_build()
	#start_cloud()
	#get_sync_srv_status()
	#print get_config_srv_status("2")
	#stop_nodemaster()
	#start_nodemaster()
	#haproxy()
	#status = get_srv_stop_status("SPortal")
	#print "Status returned by get_srv_stop_status:",status	
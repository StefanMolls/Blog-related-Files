from sulley import *

# s_intialize - Construct a new "session"
# s_static ("USER") - A string that is static (umutated) and does not get fuzzed
# s_delim(" ") - A delimiter that can be fuzzed. Will have different mutations than using s_string
# s_string("anonymous") - A string that will be mutated. Includes more mutations than s_delim

#-----------------------------------------------------------------------------------------
#Session paramaters 
SESSION_FILENAME = "pcmanftpd-sessesion" 	# Keeps track of the current fuzzing state
SLEEP_TIME = 0.5							# Pause between two fuzzing attempts
TIMEOUT = 5									# Fuzzer will time out after 5 seconds of no connection
CRASH_THRESHOLD = 4							# After 4 crashes parameter will be skipped

#-----------------------------------------------------------------------------------------
# Debugging / Create use case log
debugmode = 0
use_case_logfile = "pcman_all_cases.txt"
decision = raw_input("Do you want to just generate use cases(debugmode)?(y/n): ")
if decision == "y":
	debugmode = 1
	print "Start creating the use cases - will be stored in: " + use_case_logfile
else:
	print "Debugging turned off!"

use_case_number = 1 
counter = 1
def debug(construct):
	global use_case_number
	counter = 1
	while s_mutate(): # s_mutate generates the next upcoming mutation
		f = open(use_case_logfile,'ab')
		f.write("Use case =" + str(use_case_number) + ": ")
		f.write(s_render()) #s_render() represents the current mutation value
		use_case_number += 1
		counter += 1
		f.close()
	print "Construct: " + construct + "\t\t - Use Cases: " + str(counter)

#-----------------------------------------------------------------------------------------
# Grammar to be tested
s_initialize("user")
s_static("USER")
s_delim(" ",fuzzable=False)
s_string("anonymous")
s_static("\r\n")

s_initialize("pass")
s_static("PASS")
s_delim(" ",fuzzable=False)
s_string("test1234")
s_static("\r\n")

s_initialize("put")
s_static("PUT")
s_delim(" ",fuzzable=False)
s_string("anonymous")
s_static("\r\n")

s_initialize("stor")
s_static("STOR")
s_delim(" ",fuzzable=False)
s_string("AAAA")
s_static("\r\n")

s_initialize("mkd")
s_static("MKD")
s_delim(" ",fuzzable=False)
s_string("AAAA")
s_static("\r\n")

#-----------------------------------------------------------------------------------------
#Define pre_send function
def receive_ftp_banner(sock):
	sock.recv(1024)

#-----------------------------------------------------------------------------------------
#Define session
mysession = sessions.session(
	session_filename = SESSION_FILENAME,
	sleep_time=SLEEP_TIME,
	timeout=TIMEOUT,
	crash_threshold=CRASH_THRESHOLD)

mysession.pre_send = receive_ftp_banner
mysession.connect(s_get("user"))
if debugmode == 1: debug("user")

mysession.connect(s_get("user")		,s_get("pass"))
if debugmode == 1: debug("pass")

mysession.connect(s_get("pass")		,s_get("stor"))
if debugmode == 1: debug("stor")

mysession.connect(s_get("pass")		,s_get("mkd"))
if debugmode == 1: debug("mkd")

mysession.connect(s_get("pass")		,s_get("put"))
if debugmode == 1: debug("put")

#-----------------------------------------------------------------------------------------
# Draw graph representing the fuzzing paths
fh = open("session_test.udg", "w+")
fh.write(mysession.render_graph_udraw())
fh.close()

#-----------------------------------------------------------------------------------------
# Just some overview output
if debugmode == 0: 
	print "Number of mutation during one case: " + str(s_num_mutations()) + "\n"
	print "Total number of mutations:" + str(s_num_mutations()*5) + "\n"
	decision = raw_input("Do you want to continue?(y/n): ")
	if decision == "n":
		exit()

#-----------------------------------------------------------------------------------------
#Define target parameters
if debugmode == 0: 
	target = sessions.target("192.168.178.50",21)
	target.procmon = pedrpc.client("192.168.178.50",26002)
	target.netmon = pedrpc.client("127.0.0.1",26001)

	target.procmon_options = {
		"proc_name" : "pcmanftpd2.exe",
		"stop_commands" : ['wmic process where (name="pcmanftpd2.exe") call terminate'],
		"start_commands" : ['C:\\Bad_apps\\pcmanftpd2.exe']
	}
		
# Add target to the session		
if debugmode == 0: mysession.add_target(target)

#-----------------------------------------------------------------------------------------
# Lets get rollin'
if debugmode ==0:
	print "Starting fuzzing now"
	mysession.fuzz() # Starts the fuzzing process and also the web interface (http://127.0.0.1:26000) to see the current state
from sulley import *

# General Overview
# 1. Create requests (define fuzzing grammar)
# 2. Define sessions
# 3. Define target
# 4. Fuzz!

# s_intialize - Construct a new request
# s_static ("USER") - A string that is static (umutated) and does not get fuzzed
# s_delim(" ") - A delimiter that can be fuzzed. Will have different mutations than using s_string
# s_string("anonymous") - A string that will be mutated. Includes more mutations than s_delim

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
#Define pre_send function. Will be executed right after the three-way handshake
def receive_ftp_banner(sock):
	sock.recv(1024)

#-----------------------------------------------------------------------------------------
#Define session
#Session paramaters 
SESSION_FILENAME = "pcmanftpd-session" 		# Keeps track of the current fuzzing state
SLEEP_TIME = 0.5							# Pause between two fuzzing attempts
TIMEOUT = 5									# Fuzzer will time out after 5 seconds of no connection
CRASH_THRESHOLD = 4							# After 4 crashes parameter will be skipped

mysession = sessions.session(
	session_filename = SESSION_FILENAME,
	sleep_time=SLEEP_TIME,
	timeout=TIMEOUT,
	crash_threshold=CRASH_THRESHOLD)

mysession.pre_send = receive_ftp_banner
mysession.connect(s_get("user"))
mysession.connect(s_get("user")		,s_get("pass"))
mysession.connect(s_get("pass")		,s_get("stor"))
mysession.connect(s_get("pass")		,s_get("mkd"))
mysession.connect(s_get("pass")		,s_get("put"))

#-----------------------------------------------------------------------------------------
# Draw graph representing the fuzzing paths
fh = open("session_test.udg", "w+")
fh.write(mysession.render_graph_udraw())
fh.close()

#-----------------------------------------------------------------------------------------
# Just some overview output

print "Number of mutation during one case: " + str(s_num_mutations()) + "\n"
print "Total number of mutations:" + str(s_num_mutations()*5) + "\n"

decision = raw_input("Do you want to continue?(y/n): ")
if decision == "n":
	exit()

#-----------------------------------------------------------------------------------------
#Define target parameters
target = sessions.target("192.168.178.50",21)
target.procmon = pedrpc.client("192.168.178.50",26002)
target.netmon = pedrpc.client("127.0.0.1",26001)

target.procmon_options = {
	"proc_name" : "pcmanftpd2.exe",
	"stop_commands" : ['wmic process where (name="pcmanftpd2.exe") call terminate'],
	"start_commands" : ['C:\\Bad_apps\\pcmanftpd2.exe']
}
	
# Add target to the session		
mysession.add_target(target)

#-----------------------------------------------------------------------------------------
# Lets get rollin'

print "Starting fuzzing now"
mysession.fuzz() # Starts the fuzzing process and also the web interface (http://127.0.0.1:26000) to see the current state
#!c:\\python\\python.exe

# Added some custom code to extract all relevant case IDs into the specified filename
extract_filename = 'pcman_relevant_cases.txt'

import getopt
import sys
sys.path.append(r"../paimei")

import utils
import pgraph

USAGE = "\nUSAGE: crashbin_explorer.py <xxx.crashbin>"                                      \
        "\n    [-t|--test #]     dump the crash synopsis for a specific test case number"   \
        "\n    [-g|--graph name] generate a graph of all crash paths, save to 'name'.udg\n" 

#
# parse command line options.
#

try:
    if len(sys.argv) < 2:
        raise Exception

    opts, args = getopt.getopt(sys.argv[2:], "t:g:", ["test=", "graph="])
except:
    print USAGE
    sys.exit(1)

test_number = graph_name = graph = None

for opt, arg in opts:
    if opt in ("-t", "--test"):  test_number = int(arg)
    if opt in ("-g", "--graph"): graph_name  = arg

try:
    crashbin = utils.crash_binning.crash_binning()
    crashbin.import_file(sys.argv[1])
except:
    print "unable to open crashbin: '%s'." % sys.argv[1]
    sys.exit(1)

#
# display the full crash dump of a specific test case
#

if test_number:
    for bin, crashes in crashbin.bins.iteritems():
        for crash in crashes:
            if test_number == crash.extra:
                print crashbin.crash_synopsis(crash)
                sys.exit(0)

#
# display an overview of all recorded crashes.
#

if graph_name:
    graph = pgraph.graph()

for bin, crashes in crashbin.bins.iteritems():
    synopsis = crashbin.crash_synopsis(crashes[0]).split("\n")[0]

    if graph:
        crash_node       = pgraph.node(crashes[0].exception_address)
        crash_node.count = len(crashes)
        crash_node.label = "[%d] %s.%08x" % (crash_node.count, crashes[0].exception_module, crash_node.id)
        graph.add_node(crash_node)

    print "[%d] %s" % (len(crashes), synopsis)
    print "\t",

    for crash in crashes:
        if graph:
            last = crash_node.id
            for entry in crash.stack_unwind:
                address = long(entry.split(":")[1], 16)
                n = graph.find_node("id", address)

                if not n:
                    n       = pgraph.node(address)
                    n.count = 1
                    n.label = "[%d] %s" % (n.count, entry)
                    graph.add_node(n)
                else:
                    n.count += 1
                    n.label = "[%d] %s" % (n.count, entry)

                edge = pgraph.edge.edge(n.id, last)
                graph.add_edge(edge)
                last = n.id
        print "%d," % crash.extra,
        # Added some code to extract relevant crash IDs
        relevant_id = str(crash.extra)
        f = open(extract_filename,"a+")
        f.write(relevant_id)
        f.write("\n")
        f.close()
        # End of custom code
    print "\n"

if graph:
    fh = open("%s.udg" % graph_name, "w+")
    fh.write(graph.render_graph_udraw())
    fh.close()

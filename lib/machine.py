import socket
import traceback
import vmconfig
import psutil
from common import assoc_to_dict

def connect(machine):
    machine.connection.connect((machine.location, machine.port))

def execute(machine, code):
    datum = '%s' % code.encode("base64")
    machine.connection.sendall(datum+"#eos")

    inbuf = ""
    try:
        while 1:
            data = machine.connection.recv(4096)
            inbuf += data

            # If client commit to go, then move buf to data and clean it.
            # Otherwise, continue wait for client data
            if vmconfig.DEBUG:
                print "Receive data...", data
            if inbuf.strip()[-4:] == "#eos":
                data = inbuf[:-5]
                inbuf = ""
                break
            else:
                continue

    except KeyboardInterrupt, SystemExit:
        raise
    except:
        traceback.print_exc()

    return data.decode("base64")

def display(message):
    print message
    return

def sleep(seconds):
    import time
    time.sleep(seconds)
    return

def vmstatus(query, *args):
    def handle_cpu():
        results = {}
        records = psutil.cpu_times()
        results.update(assoc_to_dict([(k, getattr(records, k)) for k in records._fields]))
        return results
    def handle_memory():
        results = {
                "virtual":{}, 
                "swap":{},
                }
        virtual = psutil.virtual_memory()
        results['virtual'].update(assoc_to_dict([(k, getattr(virtual, k)) for k in virtual._fields]))
        swap = psutil.swap_memory()
        results['swap'].update(assoc_to_dict([(k, getattr(swap, k)) for k in swap._fields]))
        return results
    def handle_disk():
        results = {}
        disk = psutil.disk_usage("/")
        disk_io = psutil.disk_io_counters()
        results.update(assoc_to_dict([(k, getattr(disk, k)) for k in disk._fields]))
        results.update(assoc_to_dict([(k, getattr(disk_io, k)) for k in disk_io._fields]))
        return results
    def handle_network():
        results = {
                "counters" : {},
                "connections" : [],
                }
        counters = psutil.net_io_counters()
        connections = psutil.net_connections()
        results['counters'].update(assoc_to_dict([(k, getattr(counters, k)) for k in counters._fields]))
        for conn in connections:
            results['connections'].append(assoc_to_dict([(k, getattr(conn, k)) for k in conn._fields]))
        return results
    handlers = {
            "cpu" : handle_cpu,
            "memory" : handle_memory,
            "disk" : handle_disk,
            "network" : handle_network,
            }
    results = {}
    map(lambda q: results.update({q: handlers[q]()}), query)
    return results

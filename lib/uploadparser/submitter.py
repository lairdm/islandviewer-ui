'''
Send a submit request to islandviewer via tcp
'''

import os
import glob
import sys
import socket
import json
import base64
from django.conf import settings

default_host = settings.ISLANDVIEWER_HOST
default_port = settings.ISLANDVIEWER_PORT

def send_job(genome_data, genome_format, genome_name, email, ip_addr, host=default_host, port=default_port):
    try:
        s = connect_to_server(host, port)
    except Exception as e:
        if settings.DEBUG:
            print "Socket error: " +  str(e) + " to " + host + ":" + port
        raise Exception("Failure to submit file")

    encoded_genome = base64.urlsafe_b64encode(genome_data)

    json_obj = {'action': 'submit', 'genome_name': genome_name,
            'email': email, 'genome_data': encoded_genome,
            'genome_format': genome_format, 'ip_addr': ip_addr }

    json_str = json.dumps(json_obj)
    json_str += "\nEOF\n"

    ret = send_message(s, json_str)

    decoded_json = json.loads(ret)

    print decoded_json
    
    return decoded_json

def connect_to_server(host, port):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        if settings.DEBUG:
            print 'Failed to create socket'
        raise Exception("Socket failure", "Error creating a socket")
    
    if settings.DEBUG: 
        print 'Socket Created'
 
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
    #could not resolve
        if settings.DEBUG:
            print 'Hostname could not be resolved. Exiting'
        raise Exception("Socket failure", "Error, could not resolve host " + host)
 
    #Connect to remote server
    s.connect((remote_ip , port))

    return s

def send_message(s, message):
    
    try:
        s.sendall(message)
    except socket.error:
        if settings.DEBUG:
            print "Send failed"
        raise Exception("Socket failure", "Error sending message to server")

    #Now receive data
    reply = s.recv(4096)

    return reply

if __name__ == "__main__":
    
    goback = True
    while(goback):
        genome_file = raw_input("genome file name:")
        print "Use {0}?".format(genome_file)
        cont = raw_input("(Y/N)")
        if (cont.lower()=='y'):
            goback=False
        else:
            genome_file = ''

    with open(genome_file, 'r') as file_handle:
        genome_data = file_handle.read()

    send_job(genome_data, 'gbk', 'custom geneome', 'lairdm@sfu.ca')

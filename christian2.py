#!/usr/bin/env python3
# This module defines general functions for establishing an arbitrary TCP connection with a remote host

import socket
import ssl
import sys
from html.parser import HTMLParser

count = 0 # with this counter variable we are tracking the amount of links
response_dict = {} #global dictionary for storing the links

#
class WebHTMLParser(HTMLParser):



    def handle_starttag(self, tag, attrs):
        """
        Filters out links of requested page and transmits them to global dictionary

        prerequisite set for handle_starttag method,a link has to contain at least one dot,
        and/or a http or https prefix, www is not included, because it will be recognized along with the dot

        transfers ordered links for global dictionary
        {num_link: link address}
        """
        global count
        global response_dict
        if tag == 'a' :
            # we are increasing it by 1 for the correct order of the links (number is matched with nth link)
            count += 1
            # create a dictionary with count as key and the name of the link as value
            attrs = {count: v for (k, v) in attrs}
            # if something is not a link, subtract the count with 1 e.g. <a href="example.com"  target="_blank">
            if not attrs[count].startswith("http://") and not attrs[count].startswith("https://") and not "." in attrs[count]:
                count = count - 1
            elif attrs[count].startswith("http://"):
                attrs[count] = attrs[count].removeprefix("http://")
                response_dict[count] = attrs[count] # insert this key,value pair to the global dictionary
            elif attrs[count].startswith("https://"):
                #attrs[count] = attrs[count].removeprefix("https://")
                response_dict[count] = attrs[count] # insert this key, value pair to the global dictionary with prefix
            elif "." in attrs[count]:
                response_dict[count] = attrs[count]



class HttpConnectionHelper:
    """
    Helper class for establishing a TCP connection
    """

    def __init__(self):
        """
        Constructor
        """
        self.internal_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port=80, secure=False):
        """
        Establishes a connection
        :return:
        """
        connection_port = port
        if secure:
            connection_port = 443
        self.internal_connection.connect((host, connection_port))
        if secure:
            self.internal_connection = ssl.wrap_socket(self.internal_connection, keyfile=None, certfile=None,
                                                       server_side=False, cert_reqs=ssl.CERT_NONE,
                                                       ssl_version=ssl.PROTOCOL_SSLv23)

    def send_request(self, request):
        """
        Sends an arbitrary request
        :param request: The request to send (as text)
        :return:
        """
        self.internal_connection.send(request.encode())

    def receive_response(self):
        """
        Waits and receives a response form the server
        :return:
        """
        return self.internal_connection.recv(4096)

    def close(self):
        """
        Closes the connection
        :return:
        """
        self.internal_connection.close()


if __name__ == "__main__":
    webpage_input = sys.argv[1] # captures webpage inserted by the user via terminal
    params = webpage_input.split("/", maxsplit=1) # split the input into address and request parameter
    params = [element for element in params if len(element) > 0]
    if len(params) == 2: # unpack the list into two variables if a parameter for the GET request is given
        host, address = params
        if address.endswith("/"): # remove slash if there is one at the end of the address parameter
            address = address.removesuffix("/")

    # if no request parameter present, convert the list into a string and
    # add a slash as default parameter for the GET request
    else:
        host = "".join(params)
        address = "/"
        if host.endswith("/"): # remove the slash if it is present at the end of the input
            host = host.removesuffix("/")

    # Create an instance of the HttpConnectionHelper class and connect to the input webpage
    connection_helper = HttpConnectionHelper()
    connection_helper.connect(host, 80, False)
    connection_helper.send_request(f"HEAD /{address} HTTP/1.1\r\nHost: {host}\r\n\r\n")
    head_response = connection_helper.receive_response().decode()


#Head Parser

    _,x = head_response.split('\r\n',1) #filter out the status code from the response
    raw = x.split('\r\n') # each part of the response gets transformed to an element of a list
    # filter out empty parts
    raw = [elem for elem in raw if len(elem) > 2 ]


    head_dict = {}
    for elem in raw:
        # here we split parts of response into keys and values e.g {Server: BaseHTTP/0.6 Python/3.11.5}
        elem = elem.split(': ')
        k,v = elem[0],elem[1]
        head_dict[k] = v

    for k,v in head_dict.items(): # print out head response
        print(f"{k}: {v}")


#Body Parser
    #Send a GET request and call the receive_response method two times to access the body with the links
    connection_helper.send_request(f"GET /{address} HTTP/1.1\r\nHost: {host}\r\n\r\n")
    _head_response = connection_helper.receive_response()
    body_response = connection_helper.receive_response().decode()


    parser = WebHTMLParser() # create WebHTMLParser instance to filter out links
    parser.feed(body_response) # transfer request body as input
    for k,v in response_dict.items(): # print out body response using global dictionary
        print(f"[{k}] Link {k} --> {v}")

# Getting User Input for link selection

    input_link_from_user = int(input("Please enter a Number!\nPress 0 to Exit:"))
    # ask User for a number (number decides what's going to happen) e.g 0 to Exit program

    for k, v in response_dict.items():  # execute get request or exit program (depending on input)
        if input_link_from_user == k:
            connection_helper = HttpConnectionHelper()
            connection_helper.connect(host, 80, False)
            # v - value of response_dict , host - host address extracted from user input(terminal)
            connection_helper.send_request(f"GET /{v} HTTP/1.1\r\nHost: {host}\r\n\r\n")
            response = connection_helper.receive_response()
            http_response_headers = repr(response)
            print(http_response_headers)
            response = connection_helper.receive_response()
            http_response_body = repr(response)
            print(http_response_body)
        elif input_link_from_user == 0:
            break
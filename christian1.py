#!/usr/bin/env python3
# This module defines general functions for establishing an arbitrary TCP connection with a remote host

import socket
import ssl
from html.parser import HTMLParser

count = 0 # with this counter variable we are tracking the amount of links
response_link_dict = {} #global dictionary for storing the links

#
class WebHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global count
        global response_link_dict
        if tag == 'a':
            count += 1 # we are increasing it by 1 for the correct order of the links (number is matched with nth link)
            attrs = {count: v for (k, v) in attrs} # create a dictionary with count as key and the name of the link as value
            response_link_dict[count] = attrs[count] # insert this key,value pair to the global dictionary


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
    webpage_input = input("Enter a website address without prefix") # captures http page inserted by user
    params = webpage_input.split("/", maxsplit=1) # split the input into address and request parameter
    params = [element for element in params if len(element) > 0]
    if len(params) == 2: # unpack the list into two variables if a parameter for the GET request is given
        host, address = params
        if address.endswith("/"): # remove slash if there is one at the end of the address parameter
            address = address.removesuffix("/")

    else: # if not convert the list into a string and add a slash as default for the GET request
        host = "".join(params)
        address = "/"
        if host.endswith("/"): # remove the slash if it is present at the end of the input page
            host = host.removesuffix("/")


    connection_helper = HttpConnectionHelper()
    connection_helper.connect(host, 80, False)
    connection_helper.send_request(f"GET /{address} HTTP/1.1\r\nHost: {host}\r\n\r\n")
    head_response = connection_helper.receive_response().decode()


#Head Parser

    _,x = head_response.split('\r\n',1) #filter out the status code from the response
    raw = x.split('\r\n') # each part of the response gets transformed to an element of a list
    raw = [elem for elem in raw if len(elem) > 2] # filter out empty parts from response

    head_dict = {}
    for elem in raw:
        # here we split parts of response into keys and values e.g {Server: BaseHTTP/0.6 Python/3.11.5}
        elem = elem.split(': ')
        k,v = elem[0],elem[1]
        head_dict[k] = v

    for k,v in head_dict.items(): # print out head response
        print(f"{k}: {v}")


#Body Parser

    body_response = connection_helper.receive_response().decode()

    parser = WebHTMLParser()
    parser.feed(body_response)
    for k,v in response_link_dict.items(): # print out body response using dictionary from above
        print(f"[{k}] Link {k} --> {v}")

# Getting User Input for link selection

    input_link_from_user = int(input("Please enter a Number!\nPress 0 to Exit:"))
    # ask User for a number (number decides whats gonna happen) e.g 0 to Exit program

    for k, v in response_link_dict.items():  # execute get request or exit program (depending on number)
        if input_link_from_user == k:
            connection_helper = HttpConnectionHelper()
            connection_helper.connect("localhost", 80, False)
            connection_helper.send_request(f"GET /{v} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
            response = connection_helper.receive_response()
            http_response_headers = repr(response)
            print(http_response_headers)
            response = connection_helper.receive_response()
            http_response_body = repr(response)
            print(http_response_body)
        elif input_link_from_user == 0:
            break
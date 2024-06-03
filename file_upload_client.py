#!/usr/bin/env python3
import requests as r #import installed requests module
from requests.exceptions import HTTPError #import requests exceptions
from requests.exceptions import JSONDecodeError #import requests exceptions
from requests.compat import urljoin #could be useful to create url...
import json

class Client:
    def __init__(self, serverRoot, defaultProtocol="http"):
        self.set_serverRoot(serverRoot) #nom de domaine / Domain name
        self.__defaultProtocol__ = defaultProtocol #Request protocol if not specified
        self.__r__ = None #Server response
        self.__error__ = None #errors

    #Changes the base url
    def set_serverRoot(self, serverRoot):
        self.__serverRoot__ = serverRoot

    #Creates a url out of a Client object, a route and a protocol
    def make_url(self, route=None, protocol=None):
        if protocol == None:
            protocol = self.__defaultProtocol__
        res = protocol+"://"+self.__serverRoot__
        if route != None:
            res = urljoin(res, route)
        return res

    #issues an http get request
    def get(self, route=None, payload={}, as_json=False, protocol=None):
        res = True
        try :
            # Stores in __r__ the response to the query
            if as_json: #payload sent as json object
                self.__r__ = r.get(self.make_url(route, protocol), json = json.dumps(payload))
            else: #payload sent as url variables
                self.__r__ = r.get(self.make_url(route, protocol), params = payload)
            # Deletes the last error (if an error is raised this is not executed)
            self.__error__ = None
        #possible errors
        except HTTPError as http_err:
            self.__error__ = f'HTTP error occurred: {http_err}'
            self.__r__ = None
            res = False
        except Exception as err:
            self.__error__ = f'Other error occurred: {err}'
            self.__r__ = None
            res = False
        return res

    #issues an http get request
    def post(self, route=None, data=None, protocol=None):
        res = True
        try :
            # Stores in __r__ the response to the query
            if data == None:
                self.__r__ = r.post(self.make_url(route, protocol))
            else:
                self.__r__ = r.post(self.make_url(route, protocol), json=json.dumps(data))
            # Deletes the last error (if an error is raised this is not executed)
            self.__error__ = None
        #possible errors
        except HTTPError as http_err:
            self.__error__ = f'HTTP error occurred: {http_err}'
            self.__r__ = None
            res = False
        except Exception as err:
            self.__error__ = f'Other error occurred: {err}'
            self.__r__ = None
            res = False
        return res

    def upload_file(self, filepath:str, route=None, data=None, protocol=None):
        res = True
        try :
            # Stores in __r__ the response to the query
            files = {'upload_file': open(filepath,'rb')}
            if data == None:
                self.__r__ = r.post(self.make_url(route, protocol), files=files)
            else:
                self.__r__ = r.post(self.make_url(route, protocol), files=files, json=json.dumps(data))
            # Deletes the last error (if an error is raised this is not executed)
            self.__error__ = None
        #possible errors
        except HTTPError as http_err:
            self.__error__ = f'HTTP error occurred: {http_err}'
            self.__r__ = None
            res = False
        except Exception as err:
            self.__error__ = f'Other error occurred: {err}'
            self.__r__ = None
            res = False
        return res

    #issues an http get request
    def delete(self, route=None, protocol=None):
        res = True
        try :
            # Stores in __r__ the response to the query
            self.__r__ = r.delete(self.make_url(route, protocol))
            # Deletes the last error (if an error is raised this is not executed)
            self.__error__ = None
        #possible errors
        except HTTPError as http_err:
            self.__error__ = f'HTTP error occurred: {http_err}'
            self.__r__ = None
            res = False
        except Exception as err:
            self.__error__ = f'Other error occurred: {err}'
            self.__r__ = None
            res = False
        return res

    #returns the last response to a succesful query
    def lr(self):
        return self.__r__

    #returns the last error raised by a query
    def lr_error(self):
        return self.__error__

    def lr_status_code(self):
        res = None
        if self.__r__ != None:
            res = self.__r__.status_code
        return res

    def lr_headers(self):
        res = None
        if self.__r__ != None:
            res = self.__r__.headers
        return res

    def lr_response(self):
        res = None
        if self.__r__ != None:
            if "application/json" in self.lr_headers().get('content-type'):
                try:
                    res = self.__r__.json()
                except JSONDecodeError as e:
                    res = self.__r__.text
            else:
                res = self.__r__.text
        return res

    def lr_redirections(self):
        res = None
        if self.__r__ != None:
            res = self.__r__.history
        return res

    def lr_text_response(self):
        res = None
        if self.__r__ != None:
            res = self.__r__.text
        return res

if __name__ == "__main__":
    c = Client("localhost:8080", "http")
    if c.upload_file("../TPXML/recette_sample_1.xml"):#, data=['Pierre', 'Paul', 'Jacques']):
        if c.lr_status_code() != 200:
            print(c.lr_status_code(), c.lr_response())
        else:
            print(c.lr_response())

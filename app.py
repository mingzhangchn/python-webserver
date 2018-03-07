#-*- coding: UTF-8 -*-
#!/usr/bin/python

import sys 
import os 
import ctypes 
import hashlib  
import pyDes  
import binascii
import ConfigParser
import base64
import shutil
import json

Des_Key = 'aabbccdd'

use_py_encrypt = 1

def application(environ, start_response):
    
    result = ''
    try:
        request_body = environ['wsgi.input'].read()
        if (len(request_body.split('\r\n\r\n')) == 2):
            json_str = request_body.split('\r\n\r\n')[1]
        else: 
            json_str = request_body        
        http_recv = json.loads(json_str)
        id = http_recv['id']
        m3u8 = http_recv['m3u8']
        stream_server_ip = http_recv['stream_server_ip']
        stream_server_port = http_recv['stream_server_port']
        stream_server_protocol = http_recv['stream_server_protocol']
        
        print "client Id:%s"%(id)
        print "stream_server_ip:%s"%(stream_server_ip)
        print "stream_server_port:%s"%(stream_server_port)
        print "stream_server_protocol:%s"%(stream_server_protocol)
        
        print '--------------------------'
        print m3u8
        print '--------------------------'
        m3u8_list = []
        
        index = 0;
        for line in m3u8.split("\r\n"):
            if line[-3:] == ".ts" :
                if use_py_encrypt == 1:
                    newPath = line[:-11] + id[index] + "/" + line[-11:]

                    m2 = hashlib.md5()   
                    m2.update(newPath) 
                    newName = id[index] + line[-7:-3] + m2.hexdigest()[-3:]
                    #config = ConfigParser.ConfigParser()
                    #config.read('./conf.ini')
                    #Des_Key = config.get("DES","key")
                    print newName                
                    k = pyDes.des(Des_Key.encode('ascii'))
                    EncryptStr = k.encrypt(newName.encode('ascii'))  
                    encryptName = binascii.hexlify(EncryptStr)
                else:
                    nameLen = 64
                    nameBuf = ctypes.create_string_buffer('', nameLen) 
                    slice_index = int(line.split("/")[1].split('.')[0])
                    info = line.split("/")[0]
                    relpath = ctypes.create_string_buffer(info, len(info))
                    nameTransLib = ctypes.cdll.LoadLibrary("./libpromark_convert.so")
                    nameTransLib.ProMark_ConvertFilename(int(id[index]), slice_index, relpath, nameBuf, ctypes.c_int(nameLen))
                    encryptName = ctypes.string_at(nameBuf)                    
                print (encryptName)   
                realPath = '%s://%s:%s/%s%s.ts\r\n'%(stream_server_protocol,stream_server_ip,stream_server_port,line[:-11],encryptName)
                m3u8_list.append(realPath)
                index = index + 1;
                if index >= len(id) :
                    index = 0;        
            else:
                m3u8_list.append(line + "\r\n")
            
        for item in m3u8_list:
            result = result + item
     
        #print result
                
    except Exception,e:
        print e

    start_response('200 OK', [('Content-Type', 'text/plain:charset=UTF-8')])
    return result.encode('UTF-8')


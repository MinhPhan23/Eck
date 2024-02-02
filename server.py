import socket
import sys
import os
import json
import threading
import traceback

ACCEPTED_METHOD = ('GET', 'POST', 'PUT')

INDEX_FILE = 'index.html'
ERROR_FILE = '404.html'

MIME_TYPE = {
    'json' : 'application/json',
    'html' : 'text/html',
    'js' : 'text/javascript'
}

HEADER_DICT = {
    'start' : 'HTTP/1.1 {status}\r\n',
    'length' : 'Content-Length: {length}\r\n',
    'type' : 'Content-Type: {mimeType}\r\n',
    'server' : 'Server: Momoland\r\n',
    'cookie' : 'Set-Cookie: {cookie}\r\n'
} 

dir ='./'

dbPort = 9000
dbHost = 'cormorant.cs.umanitoba.ca'

tweetId = 0

def getHead(status, length, mimeType, cookie):
    """create the header for the response

    Args:
        status (int): the status code of the response, can be 200, 400, 404
        length (int): the length of the content, can be none for status 400
        mimeType (string): mimeType of the content, can be none for status 400

    Returns:
        bytes: header in bytes
    """
    result = HEADER_DICT['start'].format(status = status)
    if length is not None:
        result += HEADER_DICT['length'].format(length = length)
    if mimeType is not None:
        result += HEADER_DICT['type'].format(mimeType = mimeType)
    if cookie is not None:
        result += HEADER_DICT['cookie'].format(cookie = cookie)
    result += '\r\n'
    return result.encode()

def getFile(absDir):
    """get the data of the file

    Args:
        absDir (string): path to the file, guarentee to exist

    Returns:
        (int, string, bytes): return a tuple of the length of the file, mimeType, and content in bytes
    """
    basename = os.path.basename(absDir)
    
    ext = basename.split('.')[1]
    file = open(absDir, 'rb')
    content = file.read()
    length = len(content)
    file.close()
    
    mimeType = MIME_TYPE[ext]
        
    return (length, mimeType, content)

def findUsername(headers):
    result = None
    if 'Cookie' in headers:
        cookieDict = {}
        cookies = headers['Cookie'].split('; ')
        for cookie in cookies:
            if cookie:
                key, value = cookie.split('=', 1)
                cookieDict[key.strip()] = value.strip()
        if 'usr' in cookieDict:
            result = cookieDict['usr']
    return result

#all method works with db return the status code for the request to db and the content

def parseDbResponse(data):
    status = 500
    tweets = b''
    response = json.loads(data.decode('utf-8'))
    if response['type'] == 'GET-RESPONSE':
        try: 
            print(response)
            tweets = json.dumps(response['value']['db']).encode()
            status = response['status']
        except json.JSONDecodeError as jde:
            print(traceback.format_exc())
    elif response['type'] == 'SET-RESPONSE':
        status = response['status']
        message = response['message']
        print(message)
    return status, tweets

def getAllTweet():
    result = b''
    status = 500
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dbSocket:
        try:
            dbSocket.connect((dbHost, dbPort))
            request = {'type' : 'GET'}
            dbSocket.sendall(json.dumps(request).encode())
            data = dbSocket.recv(1024)
            status, result = parseDbResponse(data)
        except Exception as e:
            print(traceback.format_exc())
            print('Something\'s wrong')
    return status, result

def setTweet(key, content):
    status = 500
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dbSocket:
        try:
            dbSocket.connect((dbHost, dbPort))
            request = {'type' : 'SET', 'key' : key, 'value' : content}
            dbSocket.sendall(json.dumps(request).encode())
            data = dbSocket.recv(1024)
            status = parseDbResponse(data)[0]
        except Exception as e:
            print(traceback.format_exc())
            print('Something\'s wrong')
    return status
        
#functions handling request to API path return response headers (and content)
def handleTweet(method, content, user):
    resContent = b''
    resHead = getHead(400, None, None, None)
    #connect to db and get tweet
    if method == 'GET':
        status, resContent = getAllTweet()
        length = len(resContent)
        resHead = getHead(status, length, MIME_TYPE['json'], None)
    elif method == 'POST':
        content = content.split('=')
        if content[0]=='content' and content[1] !='':
            content[1] = user + ":" + content[1]
            global tweetId
            tweetId+=1
            status = setTweet(tweetId, content[1])
            resHead = getHead(status, None, None, None)
    return resHead, resContent

def updateExistingTweet (method, content, id, user):
    #connect to db and get tweet
    resHead = getHead(400, None, None, None)
    if method == 'PUT':
        content = content.split('=')
        if content[0]=='content' and content[1] !='':
            content[1] = user + ":" + content[1]
            status = setTweet(id, content[1])
            resHead = getHead(status, None, None, None)
    return resHead

def handleLogin(method, content):
    resHead = getHead(400, None, None, None)
    print(method)
    print(content)
    if method == 'POST':
        cookie = content
        content = content.split('=')
        if content[0]=='usr' and content[1] !='':
            resHead = getHead(200, None, None, cookie)
    return resHead

def handleApiPath(method, head, content, reqDir):
    resContent = b''
    
    headerLines = head.split('\r\n')
    headers = {}
    for line in headerLines:
        if line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
            
    usr = findUsername(headers)
    if len(reqDir) in (3,4) and reqDir[2] == 'tweet':
        if usr is None:
            resHead = getHead(401, None, None, None)
        else:
            #/api/tweet/{id}
            if len(reqDir) == 4:
                id = reqDir[3]
                resHead = updateExistingTweet(method, content, id, usr)
            #/api/tweet
            else:
                resHead, resContent = handleTweet(method, content, usr)
    #api/login
    elif len(reqDir)>=3 and reqDir[2] == 'login':
        resHead = handleLogin(method, content)
    else:
        resHead = getHead(400, None, None, None)
        
    return resHead, resContent
    
def handleNonApi(method, reqDir):
    resHead = b''
    resContent = b''
    
    statusCode = 200
    if method == 'GET':
        absDir = dir
        for i in reqDir:
            absDir = os.path.join(absDir, i)
        
        if os.path.isdir(absDir) and os.path.exists(os.path.join(absDir, INDEX_FILE)):
            absDir = os.path.join(absDir, INDEX_FILE)
        elif os.path.isdir(absDir) or not os.path.exists(absDir):
            absDir = dir + ERROR_FILE
            if not os.path.exists(absDir):
                absDir = ERROR_FILE
            statusCode = 404
                
        length, mimeType, resContent= getFile(absDir)
        
        resHead = getHead(statusCode, length, mimeType, None)
    else:
        statusCode = 400
        resHead = getHead(statusCode, None, None, None)
    return resHead, resContent

def parseRequest(request):
    """parse the request from the client

    Args:
        request (string): the request from client

    Returns:
        bytes: the combine of both the file content and the header
    """
    start = request.split('\r\n', 1)
    header = start[1].split('\r\n\r\n')[0]
    content = start[1].split('\r\n\r\n')[1]
    start = start[0].split(' ')
    
    resHead = b''
    resContent = b''
    
    reqDir = start[1].split("/")
    if reqDir[1] != 'api':
        resHead, resContent = handleNonApi(start[0], reqDir)
    else:
        resHead, resContent = handleApiPath(start[0], header, content, reqDir)
            
    return (resHead+resContent)


def worker(conn, addr):
    """receive and send request to client

    Args:
        conn (): the client socket
        addr (): the client address
    """
    with conn:
        try:
            request = conn.recv(1024)
            print(request.decode('utf-8'))
            data = parseRequest(request.decode('utf-8'))
            print(data.decode('utf-8'))
            conn.sendall(data)
        except Exception as e:
            print(e)
    
def runServer(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        serverSocket.bind(('', port))
        serverSocket.listen()
        while True:
            try:
                conn, addr = serverSocket.accept()
                # keep trying until resources free up
                while True:
                    if threading.active_count() < 70:
                        theThread = threading.Thread(target=worker, args=(conn, addr))
                        theThread.start()
                        print("Running {} threads".format(threading.active_count()))
                        break
            except KeyboardInterrupt as kill:
                print('Server terminated')
                sys.exit()
            except Exception as e:
                print(traceback.format_exc())
                print('Something\'s wrong')

def main() :
    try:
        if len(sys.argv) != 2:
            raise Exception("Illegal Arguments")
        port = int(sys.argv[1])          
        runServer(port)
        
    except Exception as e:
        print(traceback.format_exc())
    
main()
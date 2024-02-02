import socket
import sys
import threading
import traceback
import json

workerList = []
roundRobin = 0
workerCount = 0

fail = {'status' : 500,
        'message' : 'Unacceaptable request'}

failSetRequest = {'type' : 'SET-RESPONSE',
                  'status' : 500,
                  'message' : 'DB error, cannot change tweet, plese try again later'}

SuccessSetRequest = {'type' : 'SET-RESPONSE',
                  'status' : 200,
                  'message' : 'The tweet sucessfully update'}

failGetRequest = {'type' : 'GET-RESPONSE',
                  'status' : 500,
                  'message' : 'Cannot get the tweet'}

def connectToWorker(request, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker:
        try: 
            worker.connect((host, port))
            worker.sendall(request)
            worker.settimeout(5.0)
            response = worker.recv(1024)
            worker.settimeout(None)
        except socket.timeout:
            response =  json.dumps(failSetRequest).encode()
        except socket.error:
            response =  json.dumps(failSetRequest).encode()
    return response

def getConnectWorker(request, index):
    response = connectToWorker(json.dumps(request).encode(),workerList[index]['host'], workerList[index]['port'])
    return response

def setConnectWorker(request):
    count = 0
    request['phase'] = 'vote'
    requestJson = json.dumps(request).encode()
    for workerServer in workerList:
        response = connectToWorker(requestJson, workerServer['host'], workerServer['port'])
        responseJson = json.loads(response.decode('utf-8'))
        if responseJson['status'] == 200:
            count+=1
        else: 
            for workerServer in workerList:
                fail = {'type' : 'FAIL',
                        'key' : request['key']}
                connectToWorker(json.dumps(fail).encode(), workerServer['host'], workerServer['port'])
            break
                
    if count==workerCount:
        count = 0
        request['phase'] = 'commit'
        requestJson = json.dumps(request).encode()
        for workerServer in workerList:
            response = connectToWorker(requestJson, workerServer['host'], workerServer['port'])
            responseJson = json.loads(response.decode('utf-8'))
            if responseJson['status'] == 500:
                break
            else:
                count+=1
        if count==workerCount:
            response = json.dumps(SuccessSetRequest).encode()
        else:
            response =  json.dumps(failSetRequest).encode()
    else:
        response = failSetRequest
        response['status'] =409
        response =  json.dumps(failSetRequest).encode()


    return response

def getWorker(conn, request, index):
    try:
        response = getConnectWorker(request, index)
        conn.sendall(response)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
            
def setWorker(conn, request):
    try:
        response = setConnectWorker(request)
        conn.sendall(response)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        
def sendFail(conn):
    try:
        conn.sendall(fail)
    except Exception as e:
        print("Something wrong with socket")
    
def workerThread(conn, roundRobin):
    with conn:
        try:
            data = conn.recv(1024)
            request = json.loads(data.decode('utf-8'))
            if request['type'] == 'SET':
                setWorker(conn, request)
            elif request['type'] == 'GET':
                getWorker(conn, request, roundRobin)
            else:
                sendFail(conn)
        except json.JSONDecodeError as jde:
                print(traceback.format_exc())
                print("bad json! no cookie!")
                print(jde)
        except ValueError as ve:
                print(traceback.format_exc())
                print("Key didn't exist")
                print(ve)

def runServer(port):
    global roundRobin
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        print(socket.gethostname())
        serverSocket.bind(('', port))
        serverSocket.listen()
        while True:
            try:
                conn, addr = serverSocket.accept()
                while True:
                    if threading.active_count() < 60:
                        try:
                            theThread = threading.Thread(target=workerThread, args=(conn, roundRobin))
                            roundRobin = (roundRobin+1)%workerCount
                            theThread.start()
                            print("Running {} threads".format(threading.active_count()))
                        except Exception as e:
                            print(traceback.format_exc())
                        break
            # keep trying until resources free up
            except KeyboardInterrupt as kill:
                print('Server terminated')
                sys.exit()
            except Exception as e:
                print(traceback.format_exc())
                print('Something\'s wrong')

def main() :
    try:
        port = int(sys.argv[1])   
        global workerList
        global workerCount
        for workerArg in sys.argv[2:]:
            workerCount+=1
            workerArg = workerArg.split(':')
            workerHost = {
                'host' : workerArg[0],
                'port' : int(workerArg[1])
            }
            workerList.append(workerHost)
        runServer(port)
        
    except Exception as e:
        print(traceback.format_exc())
        
main()
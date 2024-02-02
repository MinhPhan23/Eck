import socket
import sys
import json
import traceback

database = {}
lock = {}

jsonError = {
    'type' : 'ERROR',
    'message' :'something is wrong with the json request',
    'status' : 500
}

setResponse = {
    'type' : 'SET-RESPONSE',
    'status' : 200,
    'message' : ''
}

def handleSetResponse(status, message):
    response = setResponse
    response['status'] = status
    response['message'] = message
    return response

def handleSet(request):
    phase = request['phase']
    key = str(request['key'])
    value = request['value']
    if phase == 'vote':
        if key in lock:
            if lock[key]:
                response = handleSetResponse(409, 'The tweet cannot be updated right now please try again')
            else:
                lock[key] = True
                response = handleSetResponse(200, "The key is lock and ready to commit")
        #post
        else:
            lock[key] = True
            response = handleSetResponse(200, "The key is lock and ready to commit")
    elif phase == 'commit':
        database[key] = value
        lock[key] = False
        response = handleSetResponse(200, "The value is changed successfully")
    return response

def handleFail(request):
    key = str(request['key'])
    lock[key] = False
            
def parseRequest(request):
    response = json.dumps(jsonError).encode()
    try:
        request = json.loads(request)
        if request['type'] == 'SET':
            response = handleSet(request)
            response = json.dumps(response).encode()
        elif request['type'] == 'GET':
            # I guess you want the database?
            # You'll likely want to change this funny format
            response = {'type' : 'GET-RESPONSE',
                        'value' : {
                            'type' : 'DB',
                            'db' : database
                        },
                        'status' : 200,
                        'message' : 'The tweet is get sucessfully'
                        }
            response = json.dumps(response).encode()
        else:
            lock[str(request['key'])] = False
            response = {'type' : 'FAIL-RESPONSE',
                        'status' : 200,
                        'message' : 'Unlock value'}
            response = json.dumps(response).encode()
            
    except json.JSONDecodeError as jde:
        print("bad json! no cookie!")
        print(jde)
    except ValueError as ve:
        print("Key didn't exist")
        print(ve)
    return response

def runServer(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as workerSocket:
        print(socket.gethostname())
        workerSocket.bind(('', port))
        workerSocket.listen()
        while True:
            try:
                conn, addr = workerSocket.accept()
                # keep trying until resources free up
                with conn:
                    request = conn.recv(1024)
                    print(request.decode('utf-8'))
                    data = parseRequest(request.decode('utf-8'))
                    print(data.decode('utf-8'))
                    conn.sendall(data)
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
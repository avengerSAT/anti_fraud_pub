from websocket import create_connection
import uuid
import json


def get_token_from_bo():
    ws = create_connection("wss://manager-gtw.k.fasten.com/manager-gtw/manager")
    sequence_id = str(uuid.uuid4())
    x = '{"type": "LOGIN_MANAGER", "sequence_id": "' + sequence_id + '", "data":{"email":"v.kondratev@fasten.com", "password":"BV#1Q#3T5bf"}}'
    ws.send(x)
    mess = json.loads(ws.recv())
    ws.close()
    if mess:
        if mess['sequence_id'] == sequence_id:
            # print(mess['data']['slt'])
            return mess['data']['slt']



#токен сохрании и переиспользуй обновляй по мере не обходимости

#https://manager-http-gtw.k.fasten.com/history/api/public/v1/manager/orders/0701ea4c-c7bb-4207-ac5f-a39b73e0fd6b

def get_info_from_bo(type_ws, data_ws):
    ws = create_connection("wss://manager-gtw.k.fasten.com/manager-gtw/manager")
    sequence_id = str(uuid.uuid4())
    x = '{"api_token": "' + get_token_from_bo() + '", "type": "' + type_ws + '", "sequence_id": "' + sequence_id + '", "data": ' + data_ws + '}'
    ws.send(x)
    mess = json.loads(ws.recv())
    ws.close()
    if mess:
        if mess['sequence_id'] == sequence_id:
            if mess['data']:
                # print(mess['data']['error_code'])
                if 'error_code' in mess['data']:
                    get_token_from_bo()
                else:
                    return mess['data']
        else:
            return 'ERROR'
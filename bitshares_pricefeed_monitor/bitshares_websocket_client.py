from websocket import create_connection
import json

class RPCError(Exception):
    pass

class BitsharesWebsocketClient():
    def __init__(self, websocket_url):
        self.ws = create_connection(websocket_url)
        self.request_id = 1

    def request(self, method_name, params):
        payload = {
            'id': self.request_id,
            'method': 'call',
            'params': [
                0,
                method_name,
                params
            ]
        }
        request_string = json.dumps(payload)
        # print('> {}'.format(request_string))
        self.ws.send(request_string)
        self.request_id += 1
        reply =  self.ws.recv()
        # print('< {}'.format(reply))

        ret = {}
        try:
            ret = json.loads(reply, strict=False)
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")


        if 'error' in ret:
            if 'detail' in ret['error']:
                raise RPCError(ret['error']['detail'])
            else:
                raise RPCError(ret['error']['message'])
        else:
            return ret["result"]

    def get_object(self, object_id):
        return self.request('get_objects', [[object_id]])[0]


client = BitsharesWebsocketClient('wss://api.dex.trading')

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer


class StatisticConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'statistic'
        # group_name = 'statistic'
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        group_name = 'statistic'
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    # Receive message from webSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print('Принятие сообщение и отправка группе')
        print('Данные до обработки', text_data)
        print('Данные', message)

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',  # Здесь имя метода который будет вызван дл потребителей которые получают сообщение
                'content': message
            }
        )
        # self.send(text_data=json.dumps({'message': message}))

    # Receive message from room group
    def receive_statistic(self, event):
        print('-----------------> Обработчик принятия сообщения')
        message = event['content']
        print('Данные к отправке', message)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'content': message,
        }))

    # @classmethod
    # def receive_statistic(cls, data):
    #     pass


def send_to_group(content, name):
    """
    send_to_group(content, name='statistic')
    :param content: 
    :param name: 
    :return: 
    """
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(name, {
        'type': 'receive_statistic',
        'content': content
    })

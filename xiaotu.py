import argparse
import logging
from dingtalk_stream import AckMessage
import dingtalk_stream

from my_question_parser import *
from my_sql_search import *


def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def define_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--client_id', dest='client_id', required=True,
        help='app_key or suite_key from https://open-dev.digntalk.com'
    )
    parser.add_argument(
        '--client_secret', dest='client_secret', required=True,
        help='app_secret or suite_secret from https://open-dev.digntalk.com'
    )
    options = parser.parse_args()
    return options


class CalcBotHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self, logger: logging.Logger = None):
        super(dingtalk_stream.ChatbotHandler, self).__init__()
        if logger:
            self.logger = logger
            
        self.parser = QuestionParser()
        self.sqlsearch = SqlSearch()
        
    def chat_main(self, sent):
        answer = '您好，我是小图，希望可以帮到您。'
        # print(sent)
        res_classify = self.parser.classifier(sent)
        if not res_classify:
            return answer
        print(res_classify)
        # return res_classify
        res_sql = self.sqlsearch.parser_main(res_classify)
        
        # return res_sql
        final_answers = self.parser.search_main(res_sql, sent)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        expression = incoming_message.text.content.strip()
        try:
            # result = eval(expression)
            result = self.chat_main(expression)
        except Exception as e:
            result = 'Error: %s' % e
        self.logger.info('%s = %s' % (expression, result))
        response = result
        self.reply_text(response, incoming_message)

        return AckMessage.STATUS_OK, 'OK'

def main():
    logger = setup_logger()
    options = define_options()

    credential = dingtalk_stream.Credential(options.client_id, options.client_secret)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, CalcBotHandler(logger))
    client.start_forever()


if __name__ == '__main__':
    main()
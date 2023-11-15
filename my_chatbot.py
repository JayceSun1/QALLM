from my_question_parser import *
from my_sql_search import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.parser = QuestionParser()
        self.sqlsearch = SqlSearch()

    def chat_main(self, sent):
        answer = '您好，我是智能助理，希望可以帮到您。'
        # print(sent)
        res_classify = self.parser.classifier(sent)
        if not res_classify:
            return answer
        print(res_classify)
        # return res_classify
        try:
            res_sql = self.sqlsearch.parser_main(res_classify)
            print(res_sql)
        except Exception as e:
            print("---")

        # return res_sql
        try:
            final_answers = self.parser.search_main(res_sql, sent)
            if not final_answers:
                return answer
            else:
                return '\n'.join(final_answers)
        except:
            print("123")

if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        question = input('用户:')
        answer = handler.chat_main(question)
        print('机器人:', answer)
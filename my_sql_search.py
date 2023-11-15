class SqlSearch:

    '''构建实体节点'''
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        # print("enter")
        args = res_classify['args']
        # entity_dict = self.build_entitydict(args)
        entity_dict = args
        # question_types = res_classify['question_type']
        sqls = []
        # print(entity_dict)
        sqls = self.sql_transfer(entity_dict)
#         for question_type in question_types:
#             sql_ = {}
#             sql_['question_type'] = question_type
#             sql = []
#             if question_type == 'B':
#                 sql = self.sql_transfer(question_type, entity_dict.get('Unit'))

#             elif question_type == 'C':
#                 print(entity_dict)
#                 sql = self.sql_transfer(question_type, entity_dict.get('Unit'))
                
#             elif question_type == 'D':
#                 sql = self.sql_transfer(question_type, entity_dict.get('Disaster'))
#             elif question_type == 'D':
#                 sql = self.sql_transfer(question_type, entity_dict.get('Event'))


#             if sql:
#                 sql_['sql'] = sql

#                 sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, entities):
        # if not entities:
        #     return []

        # 查询语句
        sql = {'Unit':[], 'Disaster':[], 'Event':[]}
        # 闲聊
        # if question_type == 'A':
        #     sql = ["MATCH (m:Disease) where m.name = '{0}' return m.name, m.cause".format(i) for i in entities]

        # 查询疾病的防御措施
        if entities.get('Unit') != None:
            units = entities.get('Unit')
            for unit in units:
                sql['Unit'].append(f'MATCH (m:Unit) where m.name = "{unit}" return m.name, m.duty, m.duty1, m.duty2, m.duty3, m.duty4, m.detection')

        
        # Ⅱ级应急响应时，乡镇需要做什么？
        if entities.get('Disaster') != None:
            disasters = entities.get('Disaster')
            for disaster in disasters:
                sql['Disaster'].append(f'MATCH (m:Disaster) where m.name = "{disaster}" return m.name, m.action')
        
        # 台风灾害时，需要如何处置？
        if entities.get('Event') != None:
            events = entities.get('Event')
            for event in events:
                sql['Event'].append(f'MATCH (m:Event) where m.name = "{event}" return m.name, m.desc')

       
        return sql




if __name__ == '__main__':
    handler = SqlSearch()
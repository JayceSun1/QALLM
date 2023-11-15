from langchain.chains import LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from transformers import AutoTokenizer, AutoModel, AutoConfig
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union
# from torch.mps import empty_cache
import torch
import sys
import ahocorasick
import json
import re
from py2neo import Graph


class GLM(LLM):
    max_token: int = 10000
    temperature: float = 0.001
    top_p = 0.9
    tokenizer: object = None
    model: object = None
    
    history_len: int = 1024
    
    def __init__(self):
        super().__init__()
        
    @property
    def _llm_type(self) -> str:
        return "GLM"
            
    def load_model(self, llm_device="gpu",model_name_or_path=None):
        model_config = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path,trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_name_or_path, config=model_config, trust_remote_code=True).half().cuda()

    def _call(self,prompt:str,history:List[str] = [],stop: Optional[List[str]] = None):
        response, _ = self.model.chat(
                    self.tokenizer,prompt,
                    history=history[-self.history_len:] if self.history_len > 0 else [],
                    max_length=self.max_token,temperature=self.temperature,
                    top_p=self.top_p)
        return response
    
class QuestionParser:
    def __init__(self):
        self.modelpath = "../ChatGLM3/chatglm3-6b/"
        sys.path.append(self.modelpath)
        self.llm = GLM()
        self.llm.load_model(model_name_or_path = self.modelpath)
        print(self.llm('hello'))
        self.g = Graph("http://101.43.149.186:7474", auth=("neo4j", "Stjepan1"), name='neo4j')
        self.num_limit = 20
        
    def is_letter(self, char):  
        return bool(re.match(r'[a-zA-Z]', char))

    def classifier(self, question):
        # self.prompt_classify = f"""
        # {{
        #     内容: {question}
        #     要求: 根据以上内容，你需要做意图识别，共有如下选项，单选，回答时只需返回选项前的字母即可
        #     选项: [A.闲聊,
        #     B.询问部门的职责,
        #     C.询问特定响应级别时，某个部门的职责,
        #     D.询问某自然灾害下的处置措施是什么,
        #     E.询问什么情况下启动应急响应级别]
        #     例子: ["'内容':'你好','答案':'A'", 
        #     "'内容':'水利局的职责是什么？','答案':'B'", 
        #     "'内容':'台风时乡镇的职责是什么？','答案':'C'",
        #     "'内容':'台风灾害时，需要如何处置？','答案':'D'",
        #     "'内容':'什么情况下启动Ⅰ级应急响应？','答案':'E'"]
        #     }}
        # """
        # self.cl = self.llm(self.prompt_classify)
        units=['市府办','市人武部','市委宣传部','市融媒体中心','市发改局','市经信局','市教育局','市公安局','市民政局',\
               '市财政局','市规划和自然资源局','市住建局','市交通运输局','市水利局','市农业农村局','市林业局',\
               '市商务局','市文广旅体局','市卫生健康局','市应急管理局','市城管局','杭州市生态环境局建德分局','市交投公司',\
               '市旅投公司','市城投公司','国网浙江建德市供电公司','电信建德分公司、移动建德分公司、联通建德分公司、建德华数数字电视有限公司','市气象局','市消防救援大队','乡镇']
        ds=['洪水','台风','山洪','水利工程险情','内涝','干旱']
        ds_name = ['江河洪水','台风灾害','山洪及地质灾害','水利工程险情','城市内涝','干旱灾害']
        es=[['特别重大（Ⅰ级）事件','Ⅰ','1级','一级'],['重大（Ⅱ级）事件','Ⅱ','2级','二级'],['较大（Ⅲ级）事件','Ⅲ','3级','三级'],['一般（Ⅳ级）事件','Ⅳ','4级','四级']]
        is_unit = False
        is_ds = False
        is_es = False
        Ues = []
        Des = []
        Ees = []
        for unit in units:
            if unit in question:
                is_unit = True
                if unit not in Ues:
                    Ues.append(unit) 
        for i,d in enumerate(ds):
            if d in question:
                is_ds = True
                Des.append(ds_name[i])
        for i,ee in enumerate(es):
            for e in ee:
                if e in question:
                    is_es = True
                    if es[i][0] not in Ees:
                        Ees.append(es[i][0])

        # self.cl = 'A'
        # if is_unit and not is_ds and not is_es:
        #     self.cl = 'B'
        # if is_unit and not is_ds and is_es:
        #     self.cl = 'C'
        # if is_ds:
        #     self.cl = 'D'
        # if not is_unit and not is_ds and is_es:
        #     self.cl = 'E'
        
        
        self.classify = {"args": {}}
        self.classify['args']['Unit'] = []
        for ue in Ues:
            self.classify['args']['Unit'].append(ue)
            
        self.classify['args']['Disaster'] = []
        for de in Des:
            self.classify['args']['Disaster'].append(de)
            
        self.classify['args']['Event'] = []
        for ee in Ees:
            self.classify['args']['Event'].append(ee)
        
                    
        # if self.cl == 'B':
        #     with open('unit.txt', 'r', encoding='utf-8') as f:
        #         lines = f.readlines()
        #         for line in lines:
        #             line = line[:-1]
        #             if line in question:
        #                 self.classify['args']['Unit'] = line
        #                 break
        # elif self.cl == 'C':
        #     with open('unit.txt', 'r', encoding='utf-8') as f:
        #         lines = f.readlines()
        #         for line in lines:
        #             line = line[:-1]
        #             if line in question:
        #                 self.classify['args']['Unit'] = line
        #                 break
        # elif self.cl == 'D':
        #     ds=['洪水','台风','山洪','水利工程险情','内涝','干旱']
        #     ds_name = ['江河洪水','台风灾害','山洪及地质灾害','水利工程险情','城市内涝','干旱灾害']
        #     lines = ds
        #     for i, line in enumerate(lines):
        #         if line in question:
        #             self.classify['args']['Disaster'] = ds_name[i]
        #             break
        # elif self.cl == 'E':
        #     es=[['Ⅰ','1级','一级'],['Ⅱ','2级','二级'],['Ⅲ','3级','三级'],['Ⅳ','4级','四级']]
        #     es_name = ['特别重大（Ⅰ级）事件','重大（Ⅱ级）事件','较大（Ⅲ级）事件','较大（Ⅲ级）事件']
        #     lines = es
        #     f = False
        #     for i, line in enumerate(lines):
        #         for l in line:
        #             if l in question:
        #                 f = True
        #                 self.classify['args']['Event'] = es_name[i]
        #                 break
        #         if f == True:
        #             break
        # self.classify['question_type'] = self.cl
        return self.classify
#         result = ""
#         for char in self.cl:  
#             if self.is_letter(char):  
#                 result += char.upper()
#         self.cl = result
#         self.classify = self.llm(f"""

#     {{
#         内容: {question}
#         要求: 请严格根据选项，找出内容中的实体名与实体类别，宁缺毋滥，用json格式回答。
#         选项: {{"实体选项":{{"Unit": ["水利局","乡镇","市防指"], "Event": ["Ⅱ级应急响应","Ⅲ级应急响应"，"Ⅳ级应急响应"]}},"实体类别选项": ["Unit","Event"]}}
#         例子: {{["例如对于这句话，“Ⅲ级应急响应时，水利局需要做什么？”,你应该按如下格式输出：{{"args": {{"水利局": ["Unit"], "Ⅲ级应急响应":["Event"]}}", "例如对于这句话，“何时启动Ⅲ级应急响应？”,你应该按如下格式输出：{{"args": {{"Ⅲ级应急响应": ["Event"]}}"]}}
#     }}
    
# """)
        # self.classify = json.loads(self.classify)
        # self.classify['question_types'] = [self.cl]
        # return self.classify
    
    def search_main(self, sqls, question):
        final_answers = []

        # v=json.loads(v)
        unit_querys = sqls['Unit']
        disaster_querys = sqls['Disaster']
        event_querys = sqls['Event']
        units = []
        disasters = []
        events = []
        for unit_query in unit_querys:
            # print(unit_query)
            content=self.g.run(unit_query).data()
            u = {}
            u['name'] = content[0]['m.name']
            u['duty'] = content[0]['m.duty']
            sd1 = ''
            for i, d1 in enumerate(content[0]['m.duty1']):
                sd1 += '(' + str(i + 1) + ')'
                sd1 += d1
                sd1 += '\n'
            u['duty1'] = sd1
            sd2 = ''
            for i, d2 in enumerate(content[0]['m.duty2']):
                sd2 += '(' + str(i + 1) + ')'
                sd2 += d2
                sd2 += '\n'
            u['duty2'] = sd2
            
            sd3 = ''
            for i, d3 in enumerate(content[0]['m.duty3']):
                sd3 += '(' + str(i + 1) + ')'
                sd3 += d3
                sd3 += '\n'
            u['duty3'] = sd3
            sd4 = ''
            for i, d4 in enumerate(content[0]['m.duty4']):
                sd4 += '(' + str(i + 1) + ')'
                sd4 += d4
                sd4 += '\n'
            u['duty4'] = sd4
            dt = ''
            for i, d in enumerate(content[0]['m.detection']):
                dt += '(' + str(i + 1) + ')'
                dt += d
                dt += '\n'
            u['detection'] = dt
            units.append(u)
        
        for disaster_query in disaster_querys:
            content=self.g.run(disaster_query).data()
            d = {}
            d['name'] = content[0]['m.name']
            d['action'] = content[0]['m.action'][0]
            disasters.append(d)
        
        for event_query in event_querys:
            content=self.g.run(event_query).data()
            e = {}
            e['name'] = content[0]['m.name']
            e['desc'] = content[0]['m.desc'][0]
            events.append(e)
        
        prompt=""
        if units != {}:
            for unit in units:
                p=f"""
                {{
                    {unit['name']}的职责:{unit['duty']}
                    启动一级应急响应时，{unit['name']}应该做:{unit['duty1']}
                    启动二级应急响应时，{unit['name']}应该做:{unit['duty2']}
                    启动三级应急响应时，{unit['name']}应该做:{unit['duty3']}
                    启动四级应急响应时，{unit['name']}应该做:{unit['duty4']}
                    预警活动时，{unit['name']}应该做:{unit['detection']}
                }}\n
                """
                prompt+=p
                # print(p)
        if disasters != {}:
            for disaster in disasters:
                p=f"""
                {{
                    发生{disaster['name']}时的应急措施是:{disaster['action']}
                }}\n
                """
                prompt+=p
        if events != {}:
            for event in events:
                p=f"""
                {{
                    已知以下任一条件满足时，应该启动{event['name']}:{event['desc']}
                }}\n
                """
                prompt+=p
        prompt += f"问题: {question}"
        print(prompt)
        final_answer = self.llm(prompt)
        if final_answer:
            final_answers.append(final_answer)
        return final_answers
        
        
        # for sql_ in sqls:
        #     question_type = sql_['question_type']
        #     queries = sql_['sql']
        #     answers = []
        #     for query in queries:
        #         ress = self.g.run(query).data()
        #         answers += ress
        #     # final_answer = self.answer_prettify(question_type, answers)
        #     pr = '出现或预报将出现以下情况之一者，为一般（Ⅳ级）事件：\n'
        #     for i, row in enumerate(ress):
        #         pr += str(i + 1)
        #         pr += '.'
        #         pr += row['n.name']
        #         pr += '\n'
        #     question = "什么情况下启动Ⅳ级应急响应？"
        #     prompt=f"这是关于救灾的紧急问题，你需要根据背景信息，简介专业地回答问题,不要回答任何'根据您提供的信息'之类的赘语\n问题: {question}\n背景信息: {pr}"
        #     final_answer = self.llm(prompt)
        #     if final_answer:
        #         final_answers.append(final_answer)
        # return final_answers
    
        
        
        
if __name__ == '__main__':
    handler = QuestionParser()
    res = handler.classifier('何时启动Ⅳ级应急响应？')
    # while True:
    #     x=input()
    #     res = handler.classifier(x)
    #     print(res)
    #     handler.search_main(res)
    print(res)
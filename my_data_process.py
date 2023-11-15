import json



def read_bracket(s):
    dn=''
    for i, c in enumerate(s):
        # print(i, c)
        if c.isdigit() or c=='\n' or c==' ' or c == '.':
            continue
        else:
            dn = s[i:s[i:].find('\n') + i]
            break
    l = []
    j = 0
    for i, c in enumerate(s):
        if j != 0:
            # print(s[i])
            j -= 1
            continue
        if s[i] == '（' and (i < len(s) - 2 and s[i+1].isdigit()):
            yk = s[i:].find('）') + i
            # print(i + 1, yk)
            cnt = int(s[i+1: yk])
            nhh = s[yk:].find("\n") + yk
            l.append(s[yk+1: nhh])
            print(s[yk+1: nhh], nhh - i)
            j = nhh - i
    return l, dn

# disaster
def find_para55(s):
    p=[]
    j = 0
    for i, c in enumerate(s):
        if j != 0:
            j-=1
            continue
        if s[i]=='5' and s[i+1]=='.' and s[i+2] == '5' and s[i+3]=='.' and s[i+4].isdigit():
            p55x=''
            la = s[i+4]
            # print(1)
            p55 = s[i:]
            f=False
            for ii, cc in enumerate(p55):
                p55x+=p55[ii]
                if (p55[ii]=='5' and p55[ii+1]=='.' and p55[ii+2] == '5' and p55[ii+3]=='.' and p55[ii+4] != la) or \
                (p55[ii]=='5' and p55[ii+1]=='.' and p55[ii+2] == '6' and p55[ii-1]!='.'):
                    p.append(p55x[:-1])
                    j = ii - 1
                    break
                    
        if s[i]=='5' and s[i+1]=='.' and s[i+2] == '6':
            return p            
    return p

def pro_55(s):
    disasters = {}
    l = find_para55(s)
    for p in l:
        xy, name = read_bracket(p)
        disasters[name]=xy
    return disasters

# events
def find_para4(s):
    p=[]
    j = 0
    for i, c in enumerate(s):
        if j != 0:
            j-=1
            continue
        if s[i]=='4' and s[i+1]=='.' and s[i+2].isdigit():
            p4x=''
            la = s[i+2]
            # print(1)
            p4 = s[i:]
            f=False
            for ii, cc in enumerate(p4):
                p4x+=p4[ii]
                if (p4[ii]=='4' and p4[ii+1]=='.' and p4[ii+2] != la and p4[ii+3] == ' ') or \
                (p4[ii]=='5' and p4[ii-1]!='.' and p4[ii+1]=='.' and p4[ii-1]=='\n') or ii == len(p4) - 1:
                    p.append(p4x[:-1])
                    j = ii - 1
                    break
            # p.append(p4x[:-1])
                    
        if s[i]=='5' and s[i+1]=='.' and s[i+2] == '6':
            return p            
    return p
def pro_4(s):
    events = {}
    l = find_para4(s)
    # print(l[-1])
    for p in l:
        xy, name = read_bracket(p)
        events[name]=xy
    return events

# 写入图

import os
import json
from py2neo import Graph,Node

class MedicalGraph:
    def __init__(self):
        # self.data_path = './result.json'

        self.g = Graph("http://101.43.149.186:7474", auth=("neo4j", "Stjepan1"), name='neo4j')
    
    '''读取文件'''
    def read_nodes(self):
        # 共７类节点
        fp1 = open('./output_units.json', 'r', encoding='utf-8')
        units = json.load(fp1)
        fp2 = open('./output_disasters.json', 'r', encoding='utf-8')
        disasters = json.load(fp2)
        fp3 = open('./output_events.json', 'r', encoding='utf-8')
        events = json.load(fp3)
        fp4 = open('./output_leader.json', 'r', encoding='utf-8')
        leaders = json.load(fp4)
        return units, disasters, events, leaders

        '''建立节点'''
    def create_node_unit(self, label, nodes):
        count = 0
        for na in nodes:
            node = Node(label, name=na, duty=nodes[na]['duty'], duty1=nodes[na]['duty1'], duty2=nodes[na]['duty2'],\
                       duty3=nodes[na]['duty3'], duty4=nodes[na]['duty4'], detection=nodes[na]['detection'])
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return
    
    def create_node_event(self, label, nodes):
        count = 0
        for na in nodes:
            node = Node(label, name=na, desc=nodes[na])
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return
    
    def create_node_leader(self, label, nodes):
        count = 0
        print(type(nodes))
        for na in nodes:
            print(na)
            # print('enter leader', node[na]['单位名称'])
            node = Node(label, name=nodes[na]['单位名称'], duty=nodes[na]['职责'], member=str(nodes[na]['成员']),
                        nickname=na, affiliated=nodes[na]['附属单位'])
            # print(node)
            self.g.create(node)
            count += 1
            print('leader')
            print(count, len(nodes))
        return
    def create_node_disaster(self, label, nodes):
        count = 0
        for na in nodes:
            node = Node(label, name=na, action=nodes[na])
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        units, disasters, events, leaders = self.read_nodes()
        # self.create_events_nodes(event_infos)
        self.create_node_unit('Unit', units)
        self.create_node_disaster('Disaster', disasters)
        print('disaster')
        self.create_node_event('Event', events)
        print('events')
        self.create_node_leader('Leader', leaders)
        return
    
    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # print(edges)
        
        querys=[]
        for unit in edges:
            print(f"edge123:{unit}")
            if rel_name == '特定事件单位职责':
                d1=''
                for i, d in enumerate(edges[unit]['duty1']):
                    d1+='('
                    d1 += str(i+1)
                    d1 += ')'
                    d1+=d
                    d1+='\n'
                d2=''
                for i, d in enumerate(edges[unit]['duty2']):
                    d2+='('
                    d2 += str(i+1)
                    d2 += ')'
                    d2+=d
                    d2+='\n'
                d3=''
                for i, d in enumerate(edges[unit]['duty3']):
                    d3+='('
                    d3 += str(i+1)
                    d3 += ')'
                    d3+=d
                    d3+='\n'
                d4=''
                for i, d in enumerate(edges[unit]['duty4']):
                    d4+='('
                    d4 += str(i+1)
                    d4 += ')'
                    d4+=d
                    d4+='\n'
                querys.append("match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (start_node, end_node, unit, '特别重大（Ⅰ级）事件', rel_type, d1))
                querys.append("match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (start_node, end_node, unit, '重大（Ⅱ级）事件', rel_type, d2))
                querys.append("match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (start_node, end_node, unit, '较大（Ⅲ级）事件', rel_type, d3))
                querys.append("match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (start_node, end_node, unit, '一般（Ⅳ级）事件', rel_type, d4))
            elif rel_name == '单位职责':
                query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                    start_node, end_node, edge[0], edge[1], rel_type, rel_name)
       
        for query in querys:
            print(query)

        try:
            for query in querys:
                self.g.run(query)
                print(query)
                count += 1
                    # print(rel_type, count, all)
        except Exception as e:
            print("---")
                    
                    

        return
    
    '''创建实体关系边'''
    def create_graphrels(self):
        units, disasters, events, leaders = self.read_nodes()
        self.create_relationship('Unit', 'Event', units, 'unit_event', '特定事件单位职责')
        # self.create_relationship('Unit', 'Duty', rels_unit_duty, 'duty_of_unit', '单位职责')
        
handler = MedicalGraph()
print("step1:导入图谱节点中")
handler.create_graphnodes()
print("step2:导入图谱边中")      
handler.create_graphrels()

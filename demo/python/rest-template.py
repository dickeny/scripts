#!/usr/bin/python
#-*- coding: UTF-8 -*-


class QueryRender(object):
    def __init__(self, mode="test"):
        self.mode =  mode
        self.city = None
        self.school = None
    def __getitem__(self, key):
        '''__getitem__会处理a[item]的失败查询
            处理china.10086.user之类的数字时有用'''
        return "no code"
    def __getattr__(self, key):
        if self.city is None:
            self.city = key
            return self
        else:
            return self.do_query(self.city, key)
    def do_query(self, city, key):
        # balabala
        return "value"

def do_query_school(school):
    return {"name":"test_school", "phone_number":123456}
class SchoolQueryRender(QueryRender):
    '''这个是查询学校数据库'''
    def do_query(self, city, school):
        return do_query_school(school)


def do_query_person(school):
    return {"name":"wengxt", "site":"http://csslayer.tk/"}
class PersonQueryRender(QueryRender):
    '''这个是查询人口档案数据库'''
    def do_query(self, city, person):
        return do_query_person(person)

tpl='''
{{ schools.beijing.pku.phone_number }}
{{ persons.beijing.csslayer.site }}
'''

from jinja2 import Template
template = Template(tpl)
print template.render(
        schools=SchoolQueryRender(),
        persons=PersonQueryRender(),
        )



# -*- coding: utf-8 -*-
__author__ = 'ayonel'
import itertools
import json
import os
import scrapy
from scrapy import Request

class IssueSpider(scrapy.spiders.Spider):

    name = "issue" #爬虫名称
    allowed_domains = ["github.com"] #制定爬取域名
    num = 1 # 页数，默认从第一页开始
    handle_httpstatus_list = [404, 403, 401] #如果返回这个列表中的状态码，爬虫也不会终止
    output_file = open('issue.txt', "a") #输出文件
    # output_number_file = open('issue_id.txt', "a")
    
    #token列表，隐去部分
    
    token_list = [
        'ghp_mUBotsTAu4Jf5xuCwYbAqgyLQe**********',
    ]
    token_iter = itertools.cycle(token_list) #生成循环迭代器，迭代到最后一个token后，会重新开始迭代
    


    def __init__(self): #初始化
        scrapy.spiders.Spider.__init__(self)

    def __del__(self): #爬虫结束时，关闭文件
        self.output_file.close()

    def start_requests(self):
        start_urls = [] #初始爬取链接列表
        url = "https://api.github.com/repos/pytorch/pytorch/issues?per_page=99&page="+str(self.num) #第一条爬取url
        #添加一个爬取请求
        start_urls.append(scrapy.FormRequest(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'Authorization': 'token ' + next(self.token_iter),#这个字段为添加token字段
            }, callback=self.parse)) 

        return start_urls

    def yield_request(self): #定义一个生成请求函数
        url = "https://api.github.com/repos/pytorch/pytorch/issues?per_page=99&page="+str(self.num) #生成url
        #返回请求
        return Request(url,headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en',
                'Authorization': 'token ' + next(self.token_iter),
                },callback=self.parse)

    #解析函数
    def parse(self, response):
        if response.status in self.handle_httpstatus_list:#如果遇见handle_httpstatus_list中出现的状态码
            self.num += 1 #num自增，相当于直接跳过，可以输出当前url到log文件
            yield self.yield_request() #产生新的请求
            return

        json_data = json.loads(response.text) #获取json
        length = len(json_data) #获取json长度

        if self.num < 70:
            self.num = self.num + 1
            for issue in json_data:
                for label in issue['labels']:
                    if label['name'] == 'bug':
                        data = {}
                        data['number'] = issue['number']
                        data['owner'] = issue['user']['login']
                        data['title'] = issue['title']
                        data['create_time'] = issue['created_at']
                        data['update_time'] = issue['updated_at']
                        data['body'] = issue['body']
                        self.output_file.write(json.dumps(data)+'\n\n') #输出每一行，格式也为json
                        # self.output_number_file.write(str(issue['number'])+'\n')
                        
                        break;
                
            self.output_file.flush()
            yield self.yield_request() #产生新的请求

        else: #意味着爬取到最后一页
            for issue in json_data:
                for label in issue['labels']:
                    if label['name'] == 'bug':
                        data = {}
                        data['number'] = issue['number']
                        data['owner'] = issue['user']['login']
                        data['title'] = issue['title']
                        data['create_time'] = issue['created_at']
                        data['update_time'] = issue['updated_at']
                        data['body'] = issue['body']
                        self.output_file.write(json.dumps(data)+'\n\n') #输出每一行，格式也为json
                        # self.output_number_file.write(str(issue['number'])+'\n')
                        
                        break;
                
                self.output_file.write(json.dumps(data)+'\n\n')
            self.output_file.flush()
    
    
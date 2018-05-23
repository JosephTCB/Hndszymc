# coding: utf-8
from scrapy import Spider
import json, time
from scrapy.http import Request
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
from Hndszymc.items import HndszymcItem

class HnQaSpider(Spider):
	name = 'qa'
	allowed_domains = ['www.ha-l-tax.gov.cn','wsdt.ha-l-tax.gov.cn']
	start_urls = ['http://www.ha-l-tax.gov.cn/viewCmsCac.do?cacId=ff808081537d3a110153877980b709f6']
	def parse(self, response):
		url = 'http://www.ha-l-tax.gov.cn/viewCmsCac.do?cacId=ff808081537d3a110153877980b709f6'
		# chrome_options = webdriver.ChromeOptions()
		# chrome_options.add_argument('--headless')
		# chrome_options.add_argument('--disable-gpu')
		# driver = webdriver.Chrome(chrome_options=chrome_options)
		driver = webdriver.Chrome()
		driver.get(url)
		navigationlist = BeautifulSoup(driver.page_source, 'lxml').select('a.tjilanmuwz')
		for navigation in navigationlist:
			yield Request(url='http://www.ha-l-tax.gov.cn/'+navigation['href'], callback=self.second_parse)

	def second_parse(self, response):
		menulist = BeautifulSoup(response.text, 'lxml').select('a.bt')
		for menu in menulist:
			yield Request(url='http://www.ha-l-tax.gov.cn/'+menu['href'],callback=self.third_parse)

	def third_parse(self, response):
		bs = BeautifulSoup(response.text, 'lxml')
		nodelist = bs.select('li.infoListMain')
		for node in nodelist:
			href = node.a['href']
			yield Request(url=href,callback=self.final_parse)
		sel = etree.HTML(response.text)
		next = sel.xpath('//a[contains(text(),"下一页")]')
		if(len(next)==1):
			yield Request(url=next[0].get('href'),callback=self.third_parse)

	def final_parse(self, response):
		bs = BeautifulSoup(response.text, 'lxml')
		answer = bs.select('div.zw')[0].text.replace('\n','')
		question = bs.select('h1')[0].text
		item = HndszymcItem()
		item['q'] = question
		item['a'] = answer
		yield item

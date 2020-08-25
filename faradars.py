import scrapy
import pandas as pd
import logging
import re

class FaradarsSpider(scrapy.Spider):
    name = 'faradars'
    allowed_domains = ['faradars.org']
    start_urls = ['https://faradars.org/explore-topics']
    dataframe = pd.DataFrame(columns = [ 'course'])
    dataframe.to_csv('faradars_courses.csv', mode='w', encoding= 'utf-8')
    comments_df = pd.DataFrame(columns = ['course_name', 'instructor_name','price', 'email','comment','course_rating', 'course_url'])
    comments_df.to_csv('comments.csv', mode='w', encoding= 'utf-8')
    email_df = pd.DataFrame(columns = ['email'])
    email_df.to_csv('emails.csv', mode='w')
    def parse(self, response):
        topics = response.css('div.topic > a::attr(href)').extract()
        topics = [topic for topic in topics if 'http' in topic]
        # self.log(topics)
        for topic in topics:
            self.log('=========topic = {}==========='.format(topic))
            yield scrapy.Request(url = topic, callback= self.course_list_parser)
        # pass

    def course_list_parser(self, response):
        courses_url = response.css('div.landing-course-item > table > tr > td > p > a::attr(href)').extract()
        for url in courses_url:
            yield scrapy.Request(url= url, callback= self.course_parser)

    def course_parser(self, response):
        course_name = response.css('div.main-wrapper > h1::text').extract()
        course_comments_selector = response.css('ol.commentlist > li.byuser > div.comment_container > div.comment-text > div.description')
        course_comments = []
        for c in course_comments_selector:
            course_comments.append(' '.join(c.css('::text').extract()))
        instructor_name = response.css('div.about-instructor > div.about-instructor-text > a> h5::text').extract()
        instructor_name = [', '.join(instructor_name)]
        course_rating = response.css('ol.commentlist > li.byuser > div.comment_container > div.comment-text > div.star-rating ::attr(title)').extract()
        emails_raw = response.css('ol.commentlist > li::attr(class)').extract() 
        emails_raw = [email for email in emails_raw if 'comment-author' in email]
        emails = [re.search('-author-(.*) (even|odd)', email).group(1) for email in emails_raw]
        emails = list(filter(lambda e: e!=None, emails))
        if len(course_comments)==0:
            course_comments = ['NaN']
            course_rating = ['NaN']
            emails = ['Nan']
        price = response.css('div.entry-summary>p.price > b ::text').extract()  
        if len(price) ==0:
            price = response.css('div.entry-summary>p.price > span.amount ::text').extract()
        price = [' '.join(price)]
        # emails_raw = response.css('ol.commentlist > li :: attr(class)').extract()
        
        self.log('==========={},..{}=========='.format( str(len(course_comments)), str(len(emails))))
        comment_df = pd.DataFrame({'course_name' : course_name * len(course_comments),'instructor_name': instructor_name* len(course_comments), 'price':price* len(course_comments),'email':emails, 'comment': course_comments,'course_rating':course_rating, 'course_url':[response.url] * len(course_comments)})
        comment_df.to_csv('comments.csv', mode='a', encoding= 'utf-8', header = False)


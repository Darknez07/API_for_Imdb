# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import json


class MoviesSpider(CrawlSpider):
    name = "Imdb"
    allowed_domains = ["imdb.com"]
    # Request Headers Spoofed
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"
    )

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.imdb.com/search/title/?count=1000&groups=top_1000&sort=user_rating",
            headers={"User-Agent": self.user_agent},
        )

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths="//h3[@class='lister-item-header']/a"),
            callback="parse_item",
            follow=True,
            process_request="set_user_agent",
        ),
        Rule(
            LinkExtractor(
                restrict_xpaths="//div[@class='lister list detail sub-list']/following::node()[12]"
            )
        ),
    )

    def set_user_agent(self, request):
        request.headers["User-Agent"] = self.user_agent
        return request

    def parse_item(self, response):
        # Normalize space is important to strip extra spaces
        yield {
            "Title": response.xpath("//div[@class='title_wrapper']/h1/text()").get()[:-1],
            "Year": response.xpath(
                "//div[@class='title_wrapper']//span[@id='titleYear']/a/text()"
            ).get(),
            "Duration": response.xpath(
                "normalize-space(//div[@class='title_wrapper']//time/text())"
            ).get(),
            "Genre": response.xpath(
                "//div[@class='title_wrapper']//div//a[1]/text()"
            ).get(),
            "Rating": response.xpath("//div[@class='ratingValue']//span/text()").get(),
            "Raters Count": response.xpath(
                "//div[@class='imdbRating']//a/span/text()"
            ).get(),
            "Movie_Url": response.url,
            "Speciality": response.xpath(
                "normalize-space(//span[@class='awards-blurb']/b/text())"
            ).get(),
            "Recommandations": response.xpath(
                "//div[@class='rec_page']//a/img/@alt"
            ).getall(),
            "Idea": response.xpath(
                "normalize-space(//div[@id='titleStoryLine']//div[3]/text()[2])"
            ).get(),
        }
        # item = {}
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        # item['name'] = response.xpath('//div[@id="name"]').get()
        # item['description'] = response.xpath('//div[@id="description"]').get()
        # return item

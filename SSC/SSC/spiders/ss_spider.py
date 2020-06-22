import scrapy
import json

base_url = 'https://www.semanticscholar.org'
urls = ['https://www.semanticscholar.org/paper/The-Lottery-Ticket-Hypothesis%3A-Training-Pruned-Frankle-Carbin/f90720ed12e045ac84beb94c27271d6fb8ad48cf', 
        'https://www.semanticscholar.org/paper/Attention-is-All-you-Need-Vaswani-Shazeer/204e3073870fae3d05bcbc2f6a8e263d9b72e776',
        'https://www.semanticscholar.org/paper/BERT%3A-Pre-training-of-Deep-Bidirectional-for-Devlin-Chang/df2b0e26d0599ce3e70df8a9da02e51594e0e992']

class SSSpider(scrapy.Spider):
    name = 'SSSpider'

    ## Xpaths
    TITLE = "//h1/text()"
    ABSTRACT = "//meta[@name='description']/@content"
    YEAR = "//span[@data-selenium-selector='paper-year']/span/span/text()"
    AUTHORS = "//span[@class='author-list']//span/a/span/span/text()"
    REFERENCES = "//div[@class='citation-list__citations']//div/div/h2/a/@href"

    def __init__(self, start_urls=urls, max_num=2000, root='data/'):
        self.crawled = set()
        self.urls = start_urls

        self.root = root
        self.max_num = max_num


    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        if response.status == 200 and len(self.crawled) < self.max_num:
            url = response.url
            item = {
                'id': url.split('/')[-1],
                'title': response.xpath(self.TITLE).get(),
                'abstract': response.xpath(self.ABSTRACT).get(),
                'year': response.xpath(self.YEAR).get(),
                'authors': response.xpath(self.AUTHORS).getall(),
                'references': [base_url + ref for ref in response.xpath(self.REFERENCES).getall()]
            }
            json.dump(item, open(self.root + item['id'] + '.json', 'w'))
            self.crawled.update([url])
            
            for ref in item['references']:
                if ref not in self.crawled and len(self.crawled) < self.max_num:
                    yield scrapy.Request(url=ref, callback=self.parse)
                else:
                    return
        return

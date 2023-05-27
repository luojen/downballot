import scrapy
from scrapy.utils.response import open_in_browser

class SanFranciscoSpider(scrapy.Spider):
    name = "san_francisco"

    def start_requests(self):
        yield scrapy.Request(
            url="https://sf.gov/departments/department-elections"
        )

    def parse(self, response):
        url = response.xpath('//a[contains(., "Results")]').attrib["href"]
        if len(url) > 0: 
            if "html" in response.url: 
                iframe_url = response.xpath('//iframe').attrib['src']
                yield response.follow(
                    iframe_url,
                    callback=self.parse_iframe
                )
            else: 
                yield scrapy.Request(url, callback=self.parse)
        else:
            self.log("Error in finding a URL that matches the provided XPath")


    def parse_data(self, contest): 
        unparsed_options = contest.xpath('following-sibling::table/tbody/tr')
        parsed_options = {}
        for unparsed_option in unparsed_options:
            candidate = unparsed_option.xpath('td[@id="candidate"]/descendant-or-self::*/text()').get()
            votes = unparsed_option.xpath('td[@id="votes"]/text()').get()
            parsed_options[candidate] = votes
        return parsed_options 

    def parse_metadata(self, contest): 
        unparsed_options = contest.xpath('following-sibling::table/tfoot/tr')
        parsed_options = {}
        for unparsed_option in unparsed_options:
            name = unparsed_option.xpath('td/descendant-or-self::*/text()').getall()[0]
            count = unparsed_option.xpath('td/descendant-or-self::*/text()').getall()[1]
            parsed_options[name] = count
        return parsed_options            

    def parse_iframe(self, response):
        contests = response.xpath('//h4')
        for contest in contests:
            yield {
                'Race': contest.xpath('text()').get(),
                'Data': self.parse_data(contest),
                'Metadata': self.parse_metadata(contest)
            }
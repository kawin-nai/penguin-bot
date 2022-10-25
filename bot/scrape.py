import requests
import BeautifulSoup

# Scrape the website for penguin quotes
def scrape(url):
    # get the html
    html = requests.get(url).text
    # parse the html
    soup = BeautifulSoup(html, "html.parser")
    # find the div with the class "quote"
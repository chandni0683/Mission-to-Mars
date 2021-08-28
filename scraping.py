# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup 
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def scrape_all():
    # Set up Splinter
    print("inside scrape all")
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser)
    }
    print(data)
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the Mars news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=4)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first a tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    print(news_title)
    return news_title, news_p

#JPL Space Images Featured Image
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

# Mars Facts
def mars_facts():
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
      return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    html_table = df.to_html(classes=["table", "table-bordered", "table-hover", "table-striped "]).replace("<thead>", "<thead.thead-dark>")
    html_table = html_table.replace("<th></th>\n      <th>Mars</th>\n      <th>Earth</th>\n    </tr>\n    <tr>\n      <th>Description</th>\n      <th></th>\n      <th></th>\n",'<th>Description</th> <th>Mars</th> <th>Earth</th>' )
    return html_table

def hemispheres(browser):
    base_url ='https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/'
    browser.visit(f'{base_url}index.html')

    hemisphere_image_urls = []
    html = browser.html

    hemisperes_soup = soup(html, 'html.parser')
    for link in hemisperes_soup.find_all('div', class_='description'):
        a_tag = link.find('a', class_='product-item')
        url = a_tag.get('href')
        title = a_tag.get_text()

        browser.visit(f'{base_url}{url}')
        html = browser.html
        img_soup = soup(html, 'html.parser')

        a_tag = img_soup.find('div', class_='downloads').select('a')[0]
        img_url = f"{base_url}{a_tag.get('href')}"

        hemispheres = {'img_url': img_url,
                        'title': title}
        hemisphere_image_urls.append(hemispheres)
    return hemisphere_image_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
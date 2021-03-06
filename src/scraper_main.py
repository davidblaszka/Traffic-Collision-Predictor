import selenium.webdriver
from route_url_scraper import (search_route_page, 
								all_route_urls, 
								scrape_route_page, 
								scrape_ratings_by_user,
								scrape_user)
from store_in_database import (add_to_route_html_database, 
								add_to_rating_database, 
								add_to_user_html_database, 
								add_route_link_database)
import numpy as np
import pandas as pd
from pymongo import MongoClient

if __name__ == "__main__":
	# define grade search tuples 
    grades = [(800,1900), (2000,2500), 
             (2600,3100), (3100,3500), 
             (4600,5500), (6600,12400)]
    # make empty list to fill with route page urls
    route_href_list = [] 
    for grade in grades:
        query = search_route_page(grade)
    	# returns all route urls
    	route_href_list = all_route_urls(query, route_href_list, browser)
    # save link to database
    add_route_link_database({'route_urls': route_href_list})
    # get html from route page ande user page, and make rating_dict
	browser = selenium.webdriver.PhantomJS()#Firefox()
	for route_href in route_href_list:
	    star_url, route_html, route_name = scrape_route_page(route_href, browser)
	    route_html_dict = {'route': route_name, 
	    					'html': route_html,
	    					'url': route_href}
	    add_to_route_html_database(route_html_dict)
	    user_url, rating_dict = scrape_ratings_by_user(star_url, browser)
	    rating_dict['user_url'] = user_url
	    rating_dict['route'] = route_name
	    rating_dict['route_url'] = route_href 
	    add_to_rating_database(rating_dict)

	client = MongoClient('mongodb://localhost:27017/')
	db = client.ratings_info
	ratings_info = db.ratings_info
	raw_data = ratings_info.find()
	df_ratings = pd.DataFrame(list(raw_data))
	
	url_list = []
	for row in df_ratings['user_url']:
	    for url in row:
	        url_list.append(url)

	url_list_unique = np.unique(np.asarray(url_list))
	for url in url_list_unique:
	    user_dict = scrape_user(url, browser)
	    add_to_user_html_database(user_dict)
	browser.quit()
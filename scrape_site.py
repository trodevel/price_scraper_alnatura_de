#!/usr/bin/python3

'''
Scrape Site. For educational purpose only.

Copyright (C) 2021 Dr. Sergey Kolevatov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import staleness_of

import config         # DRIVER_PATH
import helpers        # find_element_by_tag_and_class_name
import product_parser # parse_product
import re

from datetime import datetime

DEBUG_CATEGORY = False

##########################################################

def accept_banner( driver ):
    element = WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
    print( "DEBUG: found banner" )

    helpers.sleep( 5 )

    print( "clicking" )

    terms_button = driver.find_element_by_id( 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll' )
    terms_button.click()

##########################################################

def harmonize_link( link ):

    if link.endswith('/'):
        return link

    return link + '/'

##########################################################

def determine_categories( driver ):

    div = driver.find_element_by_class_name( 'top-level-categories-teaser-list' )

    if div == None:
        print( "FATAL: cannot find categories" )
        exit()

    i1 = div.find_element_by_class_name( 'top-level-categories-teaser-list__container' )

    i2 = i1.find_element_by_class_name( 'top-level-categories-teaser-list__items' )

    elements = i2.find_elements_by_class_name( 'top-level-categories-teaser-list__item' )

    print( "INFO: found {} categories".format( len( elements ) ) )

    links = dict()

    for s in elements:

        s2 = s.find_element_by_tag_name( "a" )

        link = s2.get_attribute( 'href' )

        s3 = s2.find_element_by_class_name( 'top-level-category-teaser__content' )
        s4 = s3.find_element_by_class_name( 'top-level-category-teaser__title' )

        name = s4.text

        link = harmonize_link( link )

        print( "DEBUG: determine_categories: {} - {}".format( link, name ) )

        if link.find( "frische" ) == -1 and DEBUG_CATEGORY == True:
            print( "DEBUG: temporary ignoring" )
            continue

        links[ link ] = name

    return links

##########################################################

def determine_subcategories( driver ):

    d1 = driver.find_element_by_class_name( 'products-sub-categories' )

    d2 = d1.find_element_by_css_selector( "div[class='products-sub-categories__container swiper-container']" )

    d3 = d2.find_element_by_css_selector( "div[class='products-sub-categories__items swiper-wrapper']" )

    elements = d3.find_elements_by_css_selector( "div[class='products-sub-categories__item swiper-slide']" )

    print( "INFO: found {} sub categories".format( len( elements ) ) )

    links = dict()

    for s in elements:

        if helpers.does_tag_exist( s, "a" ) == False:
            print( "WARNING: element without tag 'a', ignoring" )
            continue

        s2 = s.find_element_by_tag_name( "a" )

        link = s2.get_attribute( 'href' )
        name = s2.text

        if link == None:
            print( "WARNING: empty link {}, ignoring".format( s2 ) )
            continue

        link = harmonize_link( link )

        print( "DEBUG: determine_subcategories: {} - {}".format( link, name ) )
        links[ link ] = name

    return links

##########################################################

def determine_products( driver ):

    d1 = driver.find_element_by_css_selector( "div[class='search-results-container container']" )

    d2 = d1.find_element_by_css_selector( "div[class='row search-results-wrapper']" )

    elements = d2.find_elements_by_class_name( 'search-results-item' )

    print( "INFO: found {} elements".format( len( elements ) ) )

    links = []

    for e in elements:

        e1 = e.find_element_by_class_name( 'product-card' )

        link = e1.get_attribute( 'href' )

        if link == None:
            print( "WARNING: empty link {}, ignoring".format( s2 ) )
            continue

        link = harmonize_link( link )

        print( "DEBUG: determine_products: {}".format( link ) )

        links.append( link )

    return links

##########################################################

def determine_number_of_pages( driver ):

    try:

        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pagination-wrapper"))
            )


        i2 = i1.find_element_by_id( 'pagination' )

        active = i2.find_element_by_class_name( 'active_page' )

        elems = i2.find_elements_by_class_name( 'page_button' )

        if len( elems ) == 0:
            print( "WARNING: no multiple pages found, using active page" )
            return int( active.text )

        last = elems[-1]

        return int( last.text )

    except:

        return 1

##########################################################

def extract_handle_from_url( url ):
    p = re.compile( "/([a-z_\-]*)/$" )
    result = p.search( url )
    res = result.group( 1 )
    return res

##########################################################

def parse_product( driver, f, category_handle, category_name, subcategory_handle, subcategory_name, product_url ):

    driver.get( product_url )

    helpers.wait_for_page_load( driver )

#        p = product_parser.parse_product( e )
#        line = category_handle + ';' + subcategory_handle + ';' + category_name + ';' + subcategory_name + ';' + p + "\n"
#        f.write( line )

##########################################################

def parse_page( driver, f, category_handle, category_name, subcategory_handle, subcategory_name ):

    product_urls = determine_products( driver )

    for e in product_urls:

        parse_product( driver, f, category_handle, category_name, subcategory_handle, subcategory_name, e )

    print()

##########################################################

def parse_subcategory( driver, f, category_handle, category_name, subcategory_link, subcategory_name ):

    subcategory_handle = extract_handle_from_url( subcategory_link )

    driver.get( subcategory_link )

    helpers.wait_for_page_load( driver )

    num_pages = determine_number_of_pages( driver )

    print( "INFO: number of pages {} on {}".format( num_pages, subcategory_link ) )

    page = 1

    print( "INFO: parsing page {} / {}".format( page, num_pages ) )

    parse_page( driver, f, category_handle, category_name, subcategory_handle, subcategory_name )

    page += 1

    while page <= num_pages:
        print( "INFO: parsing page {} / {}".format( page, num_pages ) )

        driver.get( subcategory_link + '?page=' + str( page ) )

        helpers.wait_for_page_load( driver )

        parse_page( driver, f, category_handle, category_name, subcategory_handle, subcategory_name )

        page += 1

##########################################################

def parse_category( driver, f, category_link, category_name ):

    category_handle = extract_handle_from_url( category_link )

    driver.get( category_link )

    helpers.wait_for_page_load( driver )

    # "angebot" page has another structure, so we'll not bother us with parsing sub-categories
    if category_link.find( "/angebot" ) != -1:
        parse_page( driver, f, category_handle, category_name, category_handle, category_name )
        return

    links = determine_subcategories( driver )

    num_links = len( links )

    i = 0

    for c, name in links.items():

        i += 1

        print( "INFO: parsing subcategory {} / {} - {}".format( i, num_links, name ) )

        parse_subcategory( driver, f, category_handle, category_name, c, helpers.to_csv_conform_string( name ) )


##########################################################

def generate_filename():
    now = datetime.now()
    d1 = now.strftime( "%Y%m%d_%H%M" )
    res = "products_" + d1 + ".csv"
    return res

##########################################################
driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY )

driver.get( 'https://www.alnatura.de/de-de/produkte/' )

accept_banner( driver )

helpers.sleep(5)

links = determine_categories( driver )

num_links = len( links )

f = open( generate_filename(), "w" )

i = 0

for c, name in links.items():

    i += 1

    print( "INFO: parsing category {} / {} - {}".format( i, num_links, name ) )

    parse_category( driver, f, c, helpers.to_csv_conform_string( name ) )

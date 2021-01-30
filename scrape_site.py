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

    d1 = driver.find_element_by_class_name( 'search-service-rsFacetedProductList' )

    d2 = d1.find_element_by_class_name( 'search-service-hideInMobileView' )

    d3 = d2.find_element_by_class_name( 'search-service-rsFacetGroupListContainer' )

    d4 = d3.find_element_by_class_name( 'search-service-navFacetGroupContainerFacetOptionList' )

    if d4 == None:
        print( "FATAL: cannot find sub-categories" )
        exit()

    d5 = d4.find_element_by_class_name( 'search-service-navFacetGroupList' )

    d6 = helpers.find_element_by_tag_and_class_name( d5, 'ul', 'search-service-rsFacetGroupContainerFacetOptionList search-service-rsFacetGroupContainerIntendedFacetOption' )

    if d6 == None:
        print( "FATAL: cannot find sub-categories" )
        exit()

    elements = d6.find_elements_by_class_name( 'search-service-rsFacetGroupContainerCategoryFacetOption' )

    print( "INFO: found {} sub categories".format( len( elements ) ) )

    links = dict()

    for s in elements:

        if helpers.does_tag_exist( s, "a" ) == False:
            print( "WARNING: element without tag 'a', ignoring" )
            continue

        s2 = s.find_element_by_tag_name( "a" )

        link = s2.get_attribute( 'href' )
        name = s2.get_attribute( 'title' )

        if link == None:
            print( "WARNING: empty link {}, ignoring".format( s2 ) )
            continue

        link = harmonize_link( link )

        print( "DEBUG: determine_subcategories: {} - {}".format( link, name ) )
        links[ link ] = name

    return links

##########################################################

def determine_number_of_pages( driver ):

    try:

        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-service-paginationContainer"))
            )

        i = driver.find_element_by_class_name( 'search-service-paginationContainer' )

        #helpers.dump_elements_by_tag_name( i, 'div' )

        # somehow the following doesn't work, so use the helper
        #div = i.find_element_by_class_name( 'search-service-paginationPagesContainer search-service-paginationPagesContainer' )

        div = helpers.find_element_by_tag_and_class_name( i, 'div', 'search-service-paginationPagesContainer search-service-paginationPagesContainer' )

        if div == None:
            print( "FATAL: cannot find pagination container" )
            exit()

        #helpers.dump_elements_by_tag_name( div, 'form' )

        elems = div.find_elements_by_tag_name( 'form' )

        if len( elems ) == 0:
            print( "FATAL: cannot find pages" )
            exit();
        last = elems[-1]

        #print( last )

        #helpers.dump_elements_by_tag_name( last, 'button' )

        button = last.find_element_by_tag_name( 'button' )

        return int( button.text )

    except:

        return 1

##########################################################

def extract_handle_from_url( url ):
    p = re.compile( "/([a-z_\-]*)/$" )
    result = p.search( url )
    res = result.group( 1 )
    return res

##########################################################

def parse_page( driver, f, category_handle, category_name, subcategory_handle, subcategory_name ):

    content = driver.find_element_by_id( 'search-service-content' )

    if content == None:
        print( "FATAL: cannot find content" )
        exit()

    elements = content.find_elements_by_class_name( 'search-service-productDetailsWrapper' )

    print( "INFO: found {} elements".format( len( elements ) ) )

    for e in elements:
        p = product_parser.parse_product( e )
        line = category_handle + ';' + subcategory_handle + ';' + category_name + ';' + subcategory_name + ';' + p + "\n"
        f.write( line )
        print( '.', end='', flush=True )

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

exit()

num_links = len( links )

f = open( generate_filename(), "w" )

i = 0

for c, name in links.items():

    i += 1

    print( "INFO: parsing category {} / {} - {}".format( i, num_links, name ) )

    parse_category( driver, f, c, helpers.to_csv_conform_string( name ) )
#!/usr/bin/python3

def parse_product_pic( product ):
    d1 = product.find_element_by_class_name( 'product-stage' )
    d2 = d1.find_element_by_class_name( 'product-stage__container' )
    d3 = d2.find_element_by_class_name( 'product-stage__image-container' )
    d4 = d3.find_element_by_class_name( 'product-stage__image' )
    img = d4.find_element_by_tag_name( 'img' )
    return img.get_attribute( "src" )

def parse_product_grammage( p ):
    elems = p.find_elements_by_class_name( 'product__storage' )

    if len( elems ) < 2:
        print( "WARNING: cannot obtain grammage" )
        return ""

    v = elems[1].text

    return v

def parse_product_price( p ):
    d = p.find_element_by_class_name( 'product__usage' )

    return d.text

def parse_product_details( product ):
    d1 = product.find_element_by_css_selector( "div[class='tab-box js-tabs']" )
    d2 = d1.find_element_by_class_name( 'tab-box__content' )
    d3 = d2.find_element_by_css_selector( "div[class='tab-box__pane tab-box__pane--features js-tabs__content']" )
    d4 = d3.find_element_by_class_name( 'tab-box__column-two' )
    d5 = d4.find_element_by_class_name( 'product__information-items' )

    b = parse_product_grammage( d5 )
    c = parse_product_price( d5 )
    return b + ";" + c

def parse_product_brand_and_name( product ):
    d1 = product.find_element_by_class_name( 'product-stage' )
    d2 = d1.find_element_by_class_name( 'product-stage__container' )
    d3 = d2.find_element_by_class_name( 'product-stage__content' )
    d4 = d3.find_element_by_class_name( 'product-stage__basic' )
    d5 = d4.find_element_by_class_name( 'product-stage__product-name' )
    d6_1 = d5.find_element_by_class_name( 'product-stage__product-brand' )

    brand = d6_1.text

    d6_2 = d5.find_element_by_class_name( 'product-stage__product-title' )
    d7 = d6_2.find_element_by_tag_name( 'span' )

    name = d7.text

    return brand + ";" + name

def parse_product( product ):

    pic = parse_product_pic( product )
    details = parse_product_details( product )
    name = parse_product_brand_and_name( product )

    res = name + ";" + details + ";" + pic

    return res.replace( "\n", "<br>" )

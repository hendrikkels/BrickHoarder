import atexit
import datetime
import re

from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup as soup
from collections import Counter
from copy import copy

from flask_app import bricklink_api, db
from flask_app.models import Set, Part, Listing

import html
import requests

color_list = None

cached_parts_set_no = None
cached_parts_list = None

set_price_guides = None
loose_parts_guides = None

# Batch process global scheduler variable
scheduler = BackgroundScheduler(daemon=True)


def get_sets_price_guide():
    global set_price_guides
    return set_price_guides


def update_color_list():
    # print('update color triggered')
    global color_list
    color_list = bricklink_api.color.get_color_list()['data']


def update_sets_price_guide():
    # print('update sets price triggered')
    global set_price_guides
    set_list = get_inventory_set_list()
    price_guides = []
    for set in set_list:
        price_guide = get_new_set_price_guide(set)
        if price_guide is not None:
            used_price_guide = get_used_set_price_guide(set)
            price_guide['item'] = set
            if price_guide['currency_code'] == 'ZAR':
                price_guide['currency_code'] = 'R'
            price_guide['min_price'] = round(float(price_guide['min_price']), 2)
            price_guide['max_price'] = round(float(price_guide['max_price']), 2)
            price_guide['avg_price'] = round(float(price_guide['avg_price']), 2)
            price_guide['qty_avg_price'] = round(float(price_guide['qty_avg_price']), 2)
            price_guide.pop('price_detail', None)
            if used_price_guide is not None:
                price_guide['avg_price_used'] = round(float(used_price_guide['avg_price']), 2)
            if price_guide['avg_price'] != 0:
                price_guides.append(price_guide)
    price_guides = sorted(price_guides, key=lambda i: i['avg_price'], reverse=True)
    set_price_guides = price_guides


def get_new_set_price_guide(set: Set):
    response = bricklink_api.catalog_item.get_price_guide("SET", no=set.no, guide_type="sold", new_or_used="N", currency_code="ZAR")
    if response['meta']['code'] != 400:
        response_data = response['data']
        return response_data
    return None


def get_used_set_price_guide(set: Set):
    response = bricklink_api.catalog_item.get_price_guide("Set", no=set.no, guide_type="sold", new_or_used="U", currency_code="ZAR")
    if response['meta']['code'] != 400:
        response_data = response['data']
        return response_data
    return None


def get_loose_parts_price_guide():
    global loose_parts_guides
    return loose_parts_guides


def update_loose_parts_price_guide():
    # print('update loose parts triggered')
    global loose_parts_guides
    parts_list = get_inventory_loose_parts()
    price_guides = []
    for part in parts_list:
        price_guide = get_part_price_guide(part)
        if price_guide is not None:
            price_guide['item'] = part
            if price_guide['currency_code'] == 'ZAR':
                price_guide['currency_code'] = 'R'
            price_guide['min_price'] = round(float(price_guide['min_price']), 2)
            price_guide['max_price'] = round(float(price_guide['max_price']), 2)
            price_guide['avg_price'] = round(float(price_guide['avg_price']), 2)
            price_guide['qty_avg_price'] = round(float(price_guide['qty_avg_price']), 2)
            price_guide['price_detail'] = 0
            if price_guide['avg_price'] != 0:
                price_guides.append(price_guide)
    price_guides = sorted(price_guides, key=lambda i: i['avg_price'], reverse=True)
    loose_parts_guides = price_guides


def get_part_price_guide(part: Part):
    response = bricklink_api.catalog_item.get_price_guide("PART", no=part.no, color_id=part.color_id, guide_type="sold", currency_code="ZAR")
    if response['meta']['code'] != 400:
        response_data = response['data']
        return response_data
    return None


def get_part_listings(part: Part, quantity):
    listings = []
    url = 'http://www.bricklink.com/search.asp'
    params = {
        'q': str(part.no),
        'sellerCountryID': 'ZA',
        'qMin': quantity,
        'pg': 1,
        'itemType': 'P',
        'colorID': part.color_id,
        'sellerLoc': 'C',
        'viewFrom': 'sf',
        'sz': 10,
        'searchSort': 'P'
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    # print(requests.get(url, params=params).url)
    html_data = requests.get(url, params=params, headers=headers).text
    results = soup(html_data, 'html.parser').findAll('td', {'valign' : 'TOP'})
    if len(results) == 0:
        # listings.append(Listing(part.no, part.color_id, quantity, 0, '', ''))
        # print('search world')
        params = {
            'q': str(part.no),
            'qMin': quantity,
            'pg': 1,
            'itemType': 'P',
            'colorID': part.color_id,
            'sellerLoc': 'C',
            'viewFrom': 'sf',
            'sz': 10,
            'searchSort': 'P'
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        # print(requests.get(url, params=params).url)
        html_data = requests.get(url, params=params, headers=headers).text
        results = soup(html_data, 'html.parser').findAll('td', {'valign' : 'TOP'})
    for r in results:
        link = r.find('a')
        price = r.findAll('b')[1].text
        # price = float()
        listing = Listing(part.no, part.color_id, quantity, price, link.text, link['href'])
        listings.append(listing)
        # print(listings)
    return listings
    # return html


def get_optimized_purchase(set_no):
    stores = []
    pieces = []
    purchase = []
    missing_parts = get_inventory_set_missing_parts(set_no)
    for part in missing_parts:
        # print(functions.get_part_listings(part))
        # print(part)
        quantity = (part.quantity + part.extra_quantity - part.owned_quantity)
        listings = get_part_listings(part, quantity)
        if len(listings) > 0:
            stores = stores + [o.name for o in listings]
            pieces.append(listings)
    best_stores = Counter(stores)
    for store, val in best_stores.most_common():
        temp_pieces = copy(pieces)
        for piece in temp_pieces:
            listing = [x for x in piece if x.name == store]
            if len(listing) > 0:
                keys = ['part', 'color', 'quantity', 'price', 'store_name', 'url']
                values = str(listing[0]).split(",")
                temp_dict = dict(zip(keys, values))
                # temp_dict['price'].replace()
                purchase.append(dict(zip(keys, values)))
                pieces.remove(piece)
    # for item in purchase:
        # print(item['part'])
        # item['part'] = get_inventory_part(set_no, item['part'], item['color'])
    return purchase


def check_set_completeness(set_no):
    set_data = get_inventory_set(set_no)
    if set_data.type == "GROUP":
        return False
    parts_list = get_inventory_set_parts(set_no)
    for part in parts_list:
        if int(part.owned_quantity) < int(part.quantity):
            return False
    return True


def check_set_extras(set_no):
    set_data = get_inventory_set(set_no)
    if set_data.type == "GROUP":
        return False
    parts_list = get_inventory_set_parts(set_no)
    for part in parts_list:
        if int(part.owned_quantity) < int(part.quantity) + int(part.extra_quantity):
            return False
    return True


def gen_thumbnail_url(type, no, color_id):
    if type == "PART":
        return 'https://www.bricklink.com/P/' + str(color_id) + '/' + str(no) + '.jpg'
    elif type == "MINIFIG":
        return 'https://www.bricklink.com/M/' + str(no) + '.jpg'
    else:
        # Standard image placeholder
        return 'https://www.bricklink.com/P/1/3003.jpg'


def get_color_data(color_id):
    color = next((color for color in color_list if color['color_id'] == color_id), None)
    if color is None:
        return {'color_id': 0, 'color_name': 'Misc.', 'color_code': 0, 'color_type': 'Misc'}
    return color


def get_set(no):
    if '-' not in str(no):
        no = "%s-1" % no
    response = bricklink_api.catalog_item.get_item("Set", no)
    # print(response)
    if response['meta']['code'] == 400:
        return None
    response_data = response['data']
    if response_data == {}:
        return None
    set = Set(no,
              html.unescape(response_data['name']),
              response_data['type'],
              response_data['category_id'],
              html.unescape(bricklink_api.category.get_category(response_data['category_id'])['data']['category_name']),
              response_data['image_url'].replace("//img.", "http://www."),
              response_data['thumbnail_url'].replace("//img.", "http://www."),
              response_data['weight'],
              response_data['dim_x'],
              response_data['dim_y'],
              response_data['dim_z'],
              response_data['year_released'],
              response_data['is_obsolete'],
              True,
              True)
    return set


def get_part(no):
    response = bricklink_api.catalog_item.get_item("Part", no)
    response_data = response['data']
    if response_data == {}:
        return None
    part = Part(response_data['no'],
                None,
                html.unescape(response_data['name']),
                response_data['type'],
                response_data['category_id'],
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                False,
                False,
                response_data['image_url'].replace("//img.", "http://www."))
    return part


def get_set_parts(no):
    if '-' not in str(no):
        no = "%s-1" % no
    global cached_parts_set_no
    global cached_parts_list
    if no == cached_parts_set_no:
        return cached_parts_list

    response = bricklink_api.catalog_item.get_subsets("Set", no, break_minifigs=True)
    # print(response)
    response_data = response['data']
    if response_data == {}:
        return None
    response_data = filter(lambda x: x['entries'][0]['item']['type'] != 'MINIFIG', response_data)
    parts_list = []
    for line in response_data:
        part_data = line['entries'][0]
        part_color_data = get_color_data(part_data['color_id'])
        part = Part(part_data['item']['no'],
                    no,
                    html.unescape(part_data['item']['name']),
                    part_data['item']['type'],
                    part_data['item']['category_id'],
                    part_data['color_id'],
                    part_color_data['color_name'],
                    part_color_data['color_code'],
                    part_color_data['color_type'],
                    part_data['quantity'],
                    int(part_data['quantity']) - int(part_data['extra_quantity']),
                    part_data['extra_quantity'],
                    part_data['is_alternate'],
                    part_data['is_counterpart'],
                    gen_thumbnail_url(part_data['item']['type'], part_data['item']['no'], part_data['color_id']))
        parts_list.append(part)
    cached_parts_set_no = no
    cached_parts_list = parts_list
    return parts_list


def get_known_part_colors(part_no):
    response = bricklink_api.catalog_item.get_known_colors("Part", no=part_no)
    known_colors = response['data']
    part_colors = []
    keys = ['id', 'name', 'image']
    if known_colors:
        for color in known_colors:
            color_item = get_color_data(color['color_id'])
            part_color = dict.fromkeys(keys, None)
            part_color['id'] = color_item['color_id']
            part_color['name'] = color_item['color_name']
            part_color['image'] = gen_thumbnail_url("PART", part_no, color_item['color_id'])
            part_colors.append(part_color)
    else:
        part_data = get_part(part_no)
        part_color = dict.fromkeys(keys, None)
        part_color['id'] = None
        part_color['name'] = None
        part_color['image'] = part_data['thumbnail_url'].replace("//img.", "http://www.")
        part_colors.append(part_color)
    return part_colors


def get_inventory_set(set_no):
    return Set.query.filter_by(no=set_no).first()


def get_inventory_set_parts(set_no):
    return Part.query.filter_by(set_no=set_no).all()


def get_inventory_set_missing_parts(set_no):
    parts_list = get_inventory_set_parts(set_no)
    missing_parts = []
    for part in parts_list:
        if part.owned_quantity < part.quantity + part.extra_quantity:
            # print(part)
            missing_parts.append(part)
    # print(missing_parts)
    return missing_parts


def get_inventory_loose_parts():
    groups = Set.query.filter_by(type="GROUP")
    loose_parts = []
    for group in groups:
        loose_parts += Part.query.filter_by(set_no=group.no).all()
    return loose_parts


def get_inventory_set_list():
    return db.session.query(Set).all()


def get_inventory_complete_set_list():
    return Set.query.filter_by(complete=True).all()


def get_inventory_incomplete_set_list():
    return Set.query.filter_by(complete=False).all()


def get_inventory_part(set_no, part_no, color_id):
    return Part.query.filter_by(set_no=set_no, no=part_no, color_id=color_id).first()


def get_inventory_parts_list():
    return db.session.query(Part).all()


def insert_inventory_set(set: Set):
    db.session.merge(set)
    db.session.commit()


def insert_inventory_part(part: Part):
    db.session.merge(part)
    set_data = Set.query.filter_by(no=part.set_no).first()
    set_data.complete = check_set_completeness(part.set_no)
    set_data.extras = check_set_extras(part.set_no)
    db.session.merge(set_data)
    return db.session.commit()


def increase_inventory_part_quantity(part: Part, quantity: int):
    part.owned_quantity += quantity


def delete_inventory_set(set_no):
    set = get_inventory_set(set_no)
    parts_list = get_inventory_set_parts(set_no)
    for part in parts_list:
        db.session.delete(part)
    db.session.delete(set)
    return db.session.commit()


def delete_inventory_part(set_no, part_no, color_id):
    part = get_inventory_part(set_no, part_no, color_id)
    db.session.delete(part)
    return db.session.commit()


# Batch processes
def start_jobs_now():
    global scheduler
    for job in scheduler.get_jobs():
        job.modify(next_run_time=datetime.datetime.now())


def update_dashboard():
    global scheduler, set_price_guides, loose_parts_guides
    # print('updating dashboard, cache cleared')
    set_price_guides = None
    loose_parts_guides = None
    scheduler.get_job(job_id="update_sets").modify(next_run_time=datetime.datetime.now())
    scheduler.get_job(job_id="update_parts").modify(next_run_time=datetime.datetime.now())


# KICK OFF BACKGROUND PROCESSES
scheduler.add_job(func=update_color_list, trigger="interval", id="update_colors", hours=3, max_instances=1)
scheduler.add_job(func=update_sets_price_guide, trigger="interval", id="update_sets", hours=1, max_instances=1)
scheduler.add_job(func=update_loose_parts_price_guide, trigger="interval", id="update_parts", hours=1, max_instances=1)

start_jobs_now()

scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

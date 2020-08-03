from flask_app import bricklink_api, db
from flask_app.models import Set, Part

color_list = bricklink_api.color.get_color_list()['data']

cached_parts_set_no = None
cached_parts_list = None


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


def get_complete_sets_price_guide():
    set_list = get_inventory_complete_set_list()
    price_guides = []
    for set in set_list:
        price_guide = get_new_set_price_guide(set)
        if price_guide is not None:
            price_guide['item'] = set
            price_guide['min_price'] = round(float(price_guide['min_price']), 2)
            price_guide['max_price'] = round(float(price_guide['max_price']), 2)
            price_guide['avg_price'] = round(float(price_guide['avg_price']), 2)
            price_guide['qty_avg_price'] = round(float(price_guide['qty_avg_price']), 2)
            price_guides.append(price_guide)
    price_guides = sorted(price_guides, key=lambda i: i['avg_price'], reverse=True)[:10]
    return price_guides


def get_incomplete_sets_price_guide():
    set_list = get_inventory_incomplete_set_list()
    price_guides = []
    for set in set_list:
        price_guide = get_used_set_price_guide(set)
        if price_guide is not None:
            price_guide['item'] = set
            price_guide['min_price'] = round(float(price_guide['min_price']), 2)
            price_guide['max_price'] = round(float(price_guide['max_price']), 2)
            price_guide['avg_price'] = round(float(price_guide['avg_price']), 2)
            price_guide['qty_avg_price'] = round(float(price_guide['qty_avg_price']), 2)
            price_guides.append(price_guide)
    price_guides = sorted(price_guides, key=lambda i: i['avg_price'], reverse=True)[:10]
    return price_guides


def get_loose_parts_price_guide():
    parts_list = get_inventory_loose_parts()
    price_guides = []
    for part in parts_list:
        price_guide = get_part_price_guide(part)
        if price_guide is not None:
            price_guide['item'] = part
            price_guide['min_price'] = round(float(price_guide['min_price']), 2)
            price_guide['max_price'] = round(float(price_guide['max_price']), 2)
            price_guide['avg_price'] = round(float(price_guide['avg_price']), 2)
            price_guide['qty_avg_price'] = round(float(price_guide['qty_avg_price']), 2)
            price_guides.append(price_guide)
    price_guides = sorted(price_guides, key=lambda i: i['avg_price'], reverse=True)[:10]
    return price_guides


def get_part_price_guide(part: Part):
    response = bricklink_api.catalog_item.get_price_guide("Part", no=part.no, guide_type='sold', new_or_used="new", currency_code='ZAR')
    if response['meta']['code'] != 400:
        response_data = response['data']
        return response_data
    return None


def get_new_set_price_guide(set: Set):
    response = bricklink_api.catalog_item.get_price_guide("Set", no=set.no, guide_type='sold', new_or_used="N", country_code='US', currency_code='ZAR')
    if response['meta']['code'] != 400:
        response_data = response['data']
        print(response_data)
        return response_data
    return None


def get_used_set_price_guide(set: Set):
    response = bricklink_api.catalog_item.get_price_guide("Set", no=set.no, guide_type='sold', new_or_used="U", country_code='US', currency_code='ZAR')
    if response['meta']['code'] != 400:
        response_data = response['data']
        print(response_data)
        return response_data
    return None


def get_set(no):
    if '-' not in str(no):
        no = "%s-1" % no
    response = bricklink_api.catalog_item.get_item("Set", no)
    response_data = response['data']
    if response_data == {}:
        return None

    print(response)
    set = Set(no,
              response_data['name'],
              response_data['type'],
              response_data['category_id'],
              bricklink_api.category.get_category(response_data['category_id'])['data']['category_name'],
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
    print(response_data)
    part = Part(response_data['no'],
                None,
                response_data['name'],
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
                    part_data['item']['name'],
                    part_data['item']['type'],
                    part_data['item']['category_id'],
                    part_data['color_id'],
                    part_color_data['color_name'],
                    part_color_data['color_code'],
                    part_color_data['color_type'],
                    part_data['quantity'] + part_data['extra_quantity'],
                    part_data['quantity'],
                    part_data['extra_quantity'],
                    part_data['is_alternate'],
                    part_data['is_counterpart'],
                    gen_thumbnail_url(part_data['item']['type'], part_data['item']['no'], part_data['color_id']))
        print(part)
        parts_list.append(part)
    cached_parts_set_no = no
    cached_parts_list = parts_list
    return parts_list


def get_known_part_colors(part_no):
    response = bricklink_api.catalog_item.get_known_colors("Part", no=part_no)
    known_colors = response['data']
    print(known_colors)
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



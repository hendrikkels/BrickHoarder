"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, bricklinkApi
from flask import render_template, request, redirect, url_for, flash
import flask
from app.models import Set, Part

###
# Routing for your application.
###

@app.route('/')
@app.route('/home')
def home():
    return render_template("dashboard.html")


@app.route('/inventory')
def inventory():
    """Render page with all bricks in user database"""
    set_list = db.session.query(Set).all()
    parts_list = db.session.query(Part).all()
    return render_template('inventory.html', set_list=set_list, parts_list=parts_list)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        # Use search form to add extra params for search
        no = request.form.get('no')
        print(no)
        if len(no) >= 3:
            return flask.redirect('/search/set=' + no)
        else:
            flash('No results found', 'error')
            return render_template('search.html', search_str=no)
    return "get rekt"

# Display a result from a set search
@app.route('/search/set=<no>', methods=['POST', 'GET'])
def search_set(no):
    # Use REST API to get set details
    set_data = bricklinkApi.getCatalogItem("SET", no)
    print(set_data)
    if set_data != {}:
        # Set variables to be displayed as result
        set_no = set_data['no']
        set_name = set_data["name"]
        set_category_id = set_data['category_id']
        set_image_url = set_data['image_url'].replace("//img.", "http://www.")
        set_weight = set_data['weight']
        set_dim_x = set_data['dim_x']
        set_dim_y = set_data['dim_y']
        set_dim_z = set_data['dim_z']
        set_year_released = set_data['year_released']
        return render_template('result.html', search_str=no, set_no=set_no, set_name=set_name,
                               set_category_id=set_category_id, set_image_url=set_image_url,
                               set_year_released=set_year_released)
    else:
        flash('No results found', 'error')
        return render_template('search.html', search_str=no)


@app.route('/add_set/<no>', methods=['POST', 'GET'])
def add_set(no):
    set_data = bricklinkApi.getCatalogItem("SET", no)
    part_data_list = bricklinkApi.getCatalogSubsets("SET", no)
    if request.method == 'POST':
        parts_check = request.form.getlist('owned_quantity')
        print(parts_check)

        is_complete = True
        i = 0
        for part_data_entry in part_data_list:
            part_data = part_data_entry['entries'][0]

            owned_quantity = int(parts_check[i])
            print(owned_quantity)
            if (owned_quantity < part_data['quantity'] + part_data['extra_quantity']):
                is_complete = False

            part = Part(part_data['item']['no'],
                        no,
                        part_data['item']['name'],
                        part_data['item']['type'],
                        part_data['item']['category_id'],
                        part_data['color_id'],
                        owned_quantity,
                        part_data['quantity'],
                        part_data['extra_quantity'],
                        part_data['is_alternate'],
                        part_data['is_counterpart'],
                        bricklinkApi.getImageURL(part_data['item']['type'], part_data['item']['no'],
                                                 part_data['color_id']))
            db.session.merge(part)
            i += 1
        set = Set(no,
                  set_data['name'],
                  set_data['type'],
                  set_data['category_id'],
                  set_data['image_url'].replace("//img.", "http://www."),
                  set_data['thumbnail_url'].replace("//img.", "http://www."),
                  set_data['weight'],
                  set_data['dim_x'],
                  set_data['dim_y'],
                  set_data['dim_z'],
                  set_data['year_released'],
                  set_data['is_obsolete'],
                  is_complete)
        db.session.merge(set)
        db.session.commit()
        flash("Set added to personal inventory", 'success')
        return redirect(url_for('inventory'))
    else:
        parts_list = []
        keys = ['no', 'name', 'type', 'category_id', 'category_id', 'color_id',
                'quantity', 'extra_quantity', 'thumbnail_url']
        for part_data_entry in part_data_list:
            part = dict.fromkeys(keys, None)
            part_data = part_data_entry['entries'][0]

            # Create a clean dictionary for each part in the set to be displayed.
            part['no'] = part_data['item']['no']
            part['name'] = part_data['item']['name']
            part['type'] = part_data['item']['type']
            part['category_id'] = part_data['item']['category_id']
            part['color_id'] = part_data['color_id']
            part['quantity'] = part_data['quantity']
            part['extra_quantity'] = part_data['extra_quantity']
            part['thumbnail_url'] = bricklinkApi.getImageURL(part['type'], part['no'], part['color_id'])
            parts_list.append(part)
        return render_template('parts_check.html', set_no=no, parts_list=parts_list)
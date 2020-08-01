from flask import render_template, request, redirect, url_for, flash
from flask_app import app, functions

search_filter = "sets"


@app.route('/')
@app.route('/home')
def home():
    complete_guides = functions.get_complete_sets_price_guide()
    incomplete_guides = functions.get_incomplete_sets_price_guide()
    loose_parts_guides = functions.get_loose_parts_price_guide()
    return render_template("dashboard.html", complete_guides=complete_guides, incomplete_guides=incomplete_guides, loose_parts_guides=loose_parts_guides)


@app.route('/inventory')
def inventory():
    """Render page with all sets in user database"""
    set_list = functions.get_inventory_set_list()
    parts_list = functions.get_inventory_parts_list()
    return render_template('inventory.html', set_list=set_list, parts_list=parts_list)


@app.route('/set/<set_no>', methods=['GET', 'POST'])
def show_set(set_no):
    if request.method == 'POST':
        new_quantity = request.form.get('quantity')
        part_no = str(request.form.get('part_no'))
        color_id = str(request.form.get('color_id'))
        part = functions.get_inventory_part(set_no=set_no, part_no=part_no, color_id=color_id)
        print(part)
        part.owned_quantity = new_quantity
        functions.insert_inventory_part(part)
    if set_no == 'lego':
        return redirect(url_for('lego_crate'))
    set_data = functions.get_inventory_set(set_no=set_no)
    parts_list = functions.get_inventory_set_parts(set_no=set_no)
    return render_template('set_info.html', set_data=set_data, parts_list=parts_list)


@app.route('/lego_crate', methods=['GET', 'POST'])
def lego_crate():
    set_data = functions.get_inventory_set(set_no='lego')
    parts_list = functions.get_inventory_set_parts(set_no='lego')
    print(set_data)
    return render_template("lego_crate.html", set_data=set_data, parts_list=parts_list)


@app.route('/remove_set/<no>', methods=['POST', 'GET'])
def remove_set(no):
    functions.delete_inventory_set(set_no=no)
    flash('Set removed from collection', 'danger')
    return redirect(url_for('inventory'))


@app.route('/remove_part/<no>', methods=['POST', 'GET'])
def remove_part(no):
    set_no = str(request.form.get('set_no'))
    color_id = str(request.form.get('color_id'))
    functions.delete_inventory_part(set_no=set_no, part_no=no, color_id=color_id)
    return redirect("/set/" + set_no)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        # Use search form to add extra params for search
        global search_filter
        search_filter = request.form.get('search_filter')
        if search_filter is None:
            search_filter = "sets"
        print(search_filter)
        no = request.form.get('no')
        if len(no) >= 2 and no is not None:
            if search_filter == "sets":
                return redirect('/search/set=' + no)
            elif search_filter == "parts":
                return redirect('/search/part=' + no)
        else:
            flash('No results found', 'error')
            return render_template('search.html', search_str=no, search_filter=search_filter)
    return "get rekt"


# Display a result from a set search
@app.route('/search/set=<no>', methods=['POST', 'GET'])
def search_set(no):
    # Get set details
    set_data = functions.get_set(no)
    print(set_data)
    if set_data is not None:
        # Set variables to be displayed as result
        results = []
        results.append(set_data)
        return render_template('search.html', search_str=no, search_filter=search_filter, results=results)
    else:
        flash('No results found', 'error')
        return render_template('search.html', search_str=no, search_filter=search_filter)


@app.route('/add_set/<no>', methods=['POST', 'GET'])
def add_set(no):
    set = functions.get_set(no)
    parts_list = functions.get_set_parts(no)

    if request.method == 'POST':
        # Submit pressed
        functions.insert_inventory_set(set)

        parts_check = request.form.getlist('owned_quantity')
        i = 0
        for part in parts_list:
            spinner_quantity = int(parts_check[i])
            part.owned_quantity = spinner_quantity
            functions.insert_inventory_part(part)
            i += 1
        flash("Set added to personal inventory", 'success')
        return redirect(url_for('inventory'))
    else:
        return render_template('add_set.html', set_no=no, parts_list=parts_list)


# Display a resultg from a part search
@app.route('/search/part=<no>', methods=['POST', 'GET'])
def search_part(no):
    part = functions.get_part(no)
    print(part)
    if part is not None:
        results = []
        results.append(part)
        return render_template('search.html', search_str=no, search_filter=search_filter, results=results)
    else:
        flash('No results found', 'error')
        return render_template('search.html', search_str=no, search_filter=search_filter)


@app.route('/add_part/<no>', methods=['POST', 'GET'])
def add_part(no):
    part = functions.get_part(no)
    if request.method == 'POST':
        # Submit pressed
        print('submitted')
        if request.form.get('color_select') is not None:
            color = eval(request.form.get('color_select'))
            color_data = functions.get_color_data(color['id'])
            color_image = color['image']
        else:
            # CHECK IF THIS WORKS
            color_data = functions.get_color_data(0)
            color_image = "helpe"
        print(color_data)
        spinner_quantity = int(request.form.get('quantity'))
        print(spinner_quantity)
        set_no = request.form.get('set_option')
        print(set_no)

        parts_list = functions.get_inventory_set_parts(set_no)
        for part in parts_list:
            if part.no == no and part.color_id == str(color_data['color_id']):
                print('contains code')
                part.set_no = set_no
                # Increase quantity
                part.owned_quantity = part.owned_quantity + spinner_quantity
                functions.insert_inventory_part(part)
                flash("Part " + no + " added to set " + set_no, 'success')
                return redirect(url_for('inventory'))

        part = functions.get_part(no)
        part.set_no = set_no
        part.color_id = color_data['color_id']
        part.color_name = color_data['color_name']
        part.color_code = color_data['color_code']
        part.color_type = color_data['color_type']
        part.owned_quantity = spinner_quantity
        part.thumbnail_url = color_image
        functions.insert_inventory_part(part)
        flash("Part " + no + " added to set " + set_no, 'success')
        return redirect(url_for('inventory'))
    else:
        part_colors = functions.get_known_part_colors(no)
        print(part_colors)
        set_list = functions.get_inventory_set_list()
        return render_template('add_part.html', part_no=no, part_color_images=part_colors, set_list=set_list)


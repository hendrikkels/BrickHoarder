from flask import render_template, request, redirect, url_for, flash, make_response
from flask_app import app, functions
import io
import csv

# Global Variables
import_sets = []
purchase = []


@app.route('/')
@app.route('/home')
def home():
    set_price_guides = functions.get_sets_price_guide()
    if set_price_guides is not None:
        set_price_guides = set_price_guides[:5]
    print(set_price_guides)
    loose_parts_guides = functions.get_loose_parts_price_guide()
    if loose_parts_guides is not None:
        loose_parts_guides = loose_parts_guides[:5]
    print(loose_parts_guides)

    # return "hi"
    return render_template("dashboard.html", set_price_guides=set_price_guides, loose_parts_guides=loose_parts_guides)


@app.route('/home/sets/', methods=['GET', 'POST'])
def home_sets():
    if request.method == "GET":
        functions.update_dashboard()
    set_price_guides = functions.get_sets_price_guide()
    # print(set_price_guides)
    # print(loose_parts_guides)
    return render_template("dashboard_sets.html", set_price_guides=set_price_guides)


@app.route('/home/parts/', methods=['GET', 'POST'])
def home_parts():
    if request.method == "GET":
        functions.update_dashboard()
    loose_parts_guides = functions.get_loose_parts_price_guide()
    # print(set_price_guides)
    # print(loose_parts_guides)
    return render_template("dashboard.html", loose_parts_guides=loose_parts_guides)


@app.route('/inventory')
def inventory():
    """Render page with all sets in user database"""
    set_list = functions.get_inventory_set_list()
    parts_list = functions.get_inventory_parts_list()
    return render_template('inventory.html', set_list=set_list, parts_list=parts_list)


@app.route('/set/<set_no>', methods=['GET', 'POST'])
def show_set(set_no):
    set_data = functions.get_inventory_set(set_no=set_no)
    if request.method == 'POST':
        new_quantity = request.form.get('quantity')
        # print(new_quantity)
        part_no = str(request.form.get('part_no'))
        color_id = str(request.form.get('color_id'))
        part = functions.get_inventory_part(set_no=set_no, part_no=part_no, color_id=color_id)
        # print(part)
        part.owned_quantity = new_quantity
        functions.insert_inventory_part(part)
        flash("Parts updated", 'success')
    if set_data.type == 'GROUP':
        return redirect("/group/" + set_data.no)
    parts_list = functions.get_inventory_set_parts(set_no=set_no)
    return render_template('set_info.html', set_data=set_data, parts_list=parts_list)


@app.route('/set/<set_no>/guide', methods=['GET', 'POST'])
def set_guide(set_no):
    global purchase 
    if not purchase:
        purchase = functions.get_optimized_purchase(set_no)
    if request.method == 'POST':
        for item in purchase:
            part = item['part']
            part.owned_quantity = part.owned_quantity + int(item['quantity'])
            # print(part.owned_quantity)
            functions.insert_inventory_part(part)
        flash("Set updated, set is now complete", 'success')
        purchase = []
        return redirect('/inventory')
    return render_template('set_guide.html', set_no=set_no, purchase=purchase)


@app.route('/group/<group_no>', methods=['GET', 'POST'])
def group(group_no):
    set_data = functions.get_inventory_set(set_no=group_no)
    parts_list = functions.get_inventory_set_parts(set_no=group_no)
    # print(set_data)
    return render_template("group_info.html", set_data=set_data, parts_list=parts_list)


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
    flash("Parts removed", 'danger')
    return redirect("/set/" + set_no)


@app.route('/import', methods=['POST', 'GET'])
def import_file():
    if request.method == 'POST':
        # print('post oen')
        # print('pls')
        f = request.files["file_name"]
        if not f:
            return "No file"

        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        # print("file contents: ", file_contents)
        # print(type(file_contents))
        # print(csv_input)
        sets = []
        for row in csv_input:
            sets.append(row[0])
        global import_sets
        import_sets = sets
        return redirect("/import/sets")
    # print("oen")
    return render_template('import.html')


@app.route('/import/sets', methods=['POST', 'GET'])
def import_file_sets():
    global import_sets
    if request.method == 'POST':
        # ADD DIE SETS NA DIE DATABASIS
        for set in import_sets:
            functions.insert_inventory_set(set)
            parts_list = functions.get_set_parts(set.no)
            # print(set.no)
            # print(parts_list)
            for part in parts_list:
                functions.insert_inventory_part(part)
        return redirect('/inventory')
    sets = []
    for no in import_sets:
        # print(no)
        cur_set = functions.get_set(no)
        if cur_set is not None:
            sets.append(cur_set)
        import_sets = sets
    return render_template('import_set_list.html', set_list=sets)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        # Use search form to add extra params for search
        no = request.form.get('no')
        if no is not None:
            return redirect('/results/query=' + no)
    return redirect(url_for('inventory'))


@app.route('/results/query=<no>')
def results(no):
    results = []
    # Get results for  set number
    set = functions.get_set(no)
    if set is not None:
        results.append(set)
    # Get results for part number
    part = functions.get_part(no)
    if part is not None:
        results.append(part)
    return render_template('search.html', search_str=no, results=results)


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


@app.route('/add_part/<no>', methods=['POST', 'GET'])
def add_part(no):
    part = functions.get_part(no)
    if request.method == 'POST':
        # Submit pressed
        # print('submitted')
        if request.form.get('color_select') is not None:
            color = eval(request.form.get('color_select'))
            color_data = functions.get_color_data(color['id'])
            color_image = color['image']
        else:
            # CHECK IF THIS WORKS
            color_data = functions.get_color_data(0)
            color_image = "helpe"
        # print(color_data)
        spinner_quantity = int(request.form.get('quantity'))
        # print(spinner_quantity)
        set_no = request.form.get('set_option')
        # print(set_no)

        parts_list = functions.get_inventory_set_parts(set_no)
        for part in parts_list:
            if part.no == no and part.color_id == str(color_data['color_id']):
                # print('contains code')
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
        # print(part_colors)
        set_list = functions.get_inventory_set_list()
        return render_template('add_part.html', part_no=no, part_color_images=part_colors, set_list=set_list)

###
# The functions below should be applicable to all Flask apps.
###
@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
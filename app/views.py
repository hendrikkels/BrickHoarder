"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import flask

from app import app, db, bricklinkApi
from flask import render_template, request, redirect, url_for, flash
from app.forms import SearchSetForm
from app.models import Set, Part


###
# Routing for your application.
###

@app.route('/')
@app.route('/home')
def home():
    """Render website's home page."""
    set_list = db.session.query(Set).all()
    return render_template('my_sets.html', set_list=set_list)


@app.route('/inventory')
def inventory():
    """Render page with all bricks in user database"""
    parts_list = db.session.query(Part).all()
    return render_template('my_bricks.html', parts_list=parts_list)


@app.route('/search', methods=['POST', 'GET'])
def search():
    search_form = SearchSetForm()
    if request.method == 'POST':
        if search_form.validate_on_submit():
            # Use search form to add extra params for search
            no = search_form.no.data
            return flask.redirect('/search/set=' + no)
    flash_errors(search_form)
    return render_template('search.html', form=search_form)


@app.route('/search/set=<no>', methods=['POST', 'GET'])
def search_set(no):
    search_form = SearchSetForm()
    # Use REST API to get set details
    set_data = bricklinkApi.getCatalogItem("SET", no)
    if set_data != {}:
        set_no = set_data['no']
        set_name = set_data['name']
        set_year = set_data['year_released']
        set_img = set_data['image_url'].replace("//img.", "http://www.")
        return render_template('result.html', form=search_form, set_no=set_no, set_name=set_name, set_data=set_data, set_year=set_year, set_img=set_img)
    else:
        flash('No results found', 'error')
        return render_template('search.html', form=search_form)


@app.route('/add_set/<no>/parts', methods=['POST', 'GET'])
def search_set_parts(no):
    search_form = SearchSetForm()
    # Use REST API to get set details
    set_data = bricklinkApi.getCatalogItem("SET", no)
    if set_data != {}:
        # Get parts
        print('bt')
    else:
        flash('No results found', 'error')
        return render_template('search.html', form=search_form)



@app.route('/add_set/<no>', methods=['POST', 'GET'])
def add_set(no):
    set_data = bricklinkApi.getCatalogItem("SET", no)
    part_data_list = bricklinkApi.getCatalogSubsets("SET", no)
    if request.method == 'POST':
        include_parts = request.form.getlist('checkbox')
        is_complete = True
        for part_data_entry in part_data_list:
            part_data = part_data_entry['entries'][0]

            owned_quantity = include_parts.count(part_data['item']['no'])
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
        return redirect(url_for('home'))
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
            for i in range(0, (part_data['quantity'] + part_data['extra_quantity'])):
                parts_list.append(part)
        return render_template('parts_check.html', set_no=no, parts_list=parts_list)


@app.route('/remove_set/<no>', methods=['POST', 'GET'])
def remove_set(no):
    set = Set.query.filter_by(no=no).first()
    parts_list = Part.query.filter_by(set_no=no).all()
    for part in parts_list:
        db.session.delete(part)
    db.session.delete(set)
    db.session.commit()
    flash('Set removed from collection', 'danger')
    return redirect(url_for('home'))


@app.route('/set/<set_no>')
def show_set(set_no):
    set_data = Set.query.filter_by(no=set_no).first()
    return render_template('display_set.html', set_data=set_data)


# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


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


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
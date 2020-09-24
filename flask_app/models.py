from flask_app import db


class Part(db.Model):
    __tablename__ = 'parts'
    no = db.Column(db.String(255), primary_key=True, nullable=False)
    set_no = db.Column(db.String(255), db.ForeignKey('sets.no'), primary_key=True, nullable=False)
    color_id = db.Column(db.String(255), primary_key=True, nullable=False)
    color_name = db.Column(db.String(255), nullable=False)
    color_code = db.Column(db.String(255), nullable=False)
    color_type = db.Column(db.String(255), nullable=False)
    name = db.Column(db.Text(150), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.String(255), nullable=False)
    owned_quantity = db.Column(db.Integer())
    quantity = db.Column(db.Integer())
    extra_quantity = db.Column(db.Integer())
    is_alternate = db.Column(db.Boolean())
    is_counterpart = db.Column(db.Boolean())
    thumbnail_url = db.Column(db.String(255))
    __table_args__ = (
        db.UniqueConstraint("no", "set_no", "color_id"),
    )

    def __init__(self, no, set_no, name, type, category_id, color_id, color_name, color_code, color_type, owned_quantity, quantity, extra_quantity, is_alternate, is_counterpart, thumbnail_url):
        self.no = no
        self.set_no = set_no
        self.name = name
        self.type = type
        self.category_id = category_id
        self.color_id = color_id
        self.color_name = color_name
        self.color_code = color_code
        self.color_type = color_type
        self.owned_quantity = owned_quantity
        self.quantity = quantity
        self.extra_quantity = extra_quantity
        self.is_alternate = is_alternate
        self.is_counterpart = is_counterpart
        self.thumbnail_url = thumbnail_url

    def __repr__(self):
        return '<Part %r>' % self.no


class Set(db.Model):
    __tablename__ = 'sets'
    no = db.Column(db.String(255), primary_key=True, nullable=False)
    name = db.Column(db.Text(150), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255))
    thumbnail_url = db.Column(db.String(255))
    weight = db.Column(db.Float())
    dim_x = db.Column(db.Float())
    dim_y = db.Column(db.Float())
    dim_z = db.Column(db.Float())
    year_released = db.Column(db.String(4))
    obsolete = db.Column(db.Boolean())
    complete = db.Column(db.Boolean(), nullable=False)
    extras = db.Column(db.Boolean(), nullable=False)
    children = db.relationship("Part")
    __table_args__ = (
        db.UniqueConstraint("no"),
    )

    def __init__(self, no, name, type, category_id, category, image_url, thumbnail_url, weight, dim_x, dim_y, dim_z, year_released, obsolete, complete, extras):
        self.no = no
        self.name = name
        self.type = type
        self.category_id = category_id
        self.category = category
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url
        self.weight = weight
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_z = dim_z
        self.year_released = year_released
        self.obsolete = obsolete
        self.complete = complete
        self.extras = extras

    def __repr__(self):
        return self.no + ", " + \
               self.name + ", "


db.create_all()


class Listing(object):

    def __init__(self, part_no, color_id, qty, price, name, link):
        self.part_no = part_no
        self.color_id = color_id
        self.qty = qty
        self.price = price
        self.name = name
        self.link = 'http://bricklink.com' + link

    def __str__(self):
        output = '{part_no},{color_id},{qty},{price},"{name}",{link}'
        return output.format(**self.__dict__)


lego_box = Set('GRP0', 'Lego Crate', 'GROUP', 'Misc.', 'Misc.',
               'https://cdn.stylepark.com/articles/2008/toy-of-the-century/v283170_958_992_800-1.jpg?mtime=20160926224251&focal=none',
               'https://cdn.stylepark.com/articles/2008/toy-of-the-century/v283170_958_992_800-1.jpg?mtime=20160926224251&focal=none',
               0, 0, 0, 0, '1932', False, False, False)
db.session.merge(lego_box)
db.session.commit()

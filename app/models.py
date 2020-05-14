from app import db


class Part(db.Model):
    __tablename__ = 'parts'
    no = db.Column(db.String(255), primary_key=True, nullable=False)
    set_no = db.Column(db.String(255), db.ForeignKey('sets.no'), primary_key=True, nullable=False)
    color_id = db.Column(db.String(255), primary_key=True, nullable=False)
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

    def __init__(self, no, set_no, name, type, category_id, color_id, owned_quantity, quantity, extra_quantity, is_alternate, is_counterpart, thumbnail_url):
        self.no = no
        self.set_no = set_no
        self.name = name
        self.type = type
        self.category_id = category_id
        self.color_id = color_id
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
    image_url = db.Column(db.String(255))
    thumbnail_url = db.Column(db.String(255))
    weight = db.Column(db.Float())
    dim_x = db.Column(db.Float())
    dim_y = db.Column(db.Float())
    dim_z = db.Column(db.Float())
    year_released = db.Column(db.String(4))
    is_obsolete = db.Column(db.Boolean())
    is_complete = db.Column(db.Boolean(), nullable=False)
    children = db.relationship("Part")
    __table_args__ = (
        db.UniqueConstraint("no"),
    )

    def __init__(self, no, name, type, category_id, image_url, thumbnail_url, weight, dim_x, dim_y, dim_z, year_released, is_obsolete, is_complete):
        self.no = no
        self.name = name
        self.type = type
        self.category_id = category_id
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url
        self.weight = weight
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_z = dim_z
        self.year_released = year_released
        self.is_obsolete = is_obsolete
        self.is_complete = is_complete

    def __repr__(self):
        return '<Set %r>' % self.no


db.create_all()
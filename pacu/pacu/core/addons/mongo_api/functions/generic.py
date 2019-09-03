import datetime
from bson import ObjectId
from mongoengine import *

import pacu.core.addons.mongo_api.models as models


def new_db(cls = None, **kwargs):
    """ Creates a new mongoengine document along with all nested documents from given kwargs.
    All document fields require a mongoengine document class specified as 'cls'.

    Args:
        cls (str): document class
        kwargs: fields to create

    Returns:
        mongoengine.Document: new model object
    """

    model = getattr(globals()['models'], cls)

    # recursively create nested documents
    for field_name, field_value in kwargs.items():

        if field_name in model._fields:
            field = model._fields[field_name]

            if isinstance(field, (ReferenceField, GenericReferenceField, EmbeddedDocument, EmbeddedDocumentField, DynamicEmbeddedDocument, GenericEmbeddedDocumentField)):
                if not isinstance(field_value, Document):
                    kwargs[field_name] = new_db(**field_value)

            if isinstance(field, ListField):
                new_vals = []
                for l in field_value:
                    if isinstance(l, dict) and 'cls' in l:
                        new_vals.append(new_db(**l))
                    else:
                        new_vals.append(l)
                kwargs[field_name] = new_vals

            if isinstance(field, MapField):
                new_vals = {}
                for key, value in field_value.items():
                    if isinstance(value, dict) and 'cls' in value:
                        new_vals[key] = (new_db(**value))
                    else:
                        new_vals[key] = value
                kwargs[field_name] = new_vals

    if isinstance(model(), Document):
        existing = model.objects(**kwargs).first()
        if existing:
            return existing  #.to_dbref()  # use ref for performance
        else:
            return model(**kwargs).save()

    # embedded document types
    else:
        return model(**kwargs)


def update_db(owner, db_id, cls, **kwargs):
    """ Updates a database document. If a dict is given in place of a reference
    the reference will be recursivly updated with the dict entries.
    dict requires a mongoengine document class specified as 'cls'.

    Args:
        owner (models.User): owner of the object
        db_id (str): document id
        cls (str): document class
        kwargs: fields to update

    Returns:
        mongoengine.Document: updated model object
    """

    model = getattr(globals()['models'], cls)
    document = model.objects.get(owner=owner, id=db_id)
    updates = {}
    for field_name, field in document._fields.items():

        if field_name in kwargs:
            if isinstance(field, ReferenceField):
                if isinstance(kwargs[field_name], dict):
                    update_db(**kwargs[field_name])
                else:
                    updates[field_name] = ObjectId(kwargs[field_name])

            elif isinstance(field, ListField):
                if len(document[field_name]) > 0 and {'id', 'cls'} <= set(kwargs[field_name][0]):
                    for item in kwargs[field_name]:
                        update_db(**item)
                else:
                    updates[field_name] = kwargs[field_name]

            elif isinstance(field, DateTimeField):
                updates[field_name] = datetime.datetime.strptime(kwargs[field_name], "%Y-%m-%dT%H:%M:%S.%f")

            else:
                updates[field_name] = kwargs[field_name]

    return model.objects.get(owner=owner, id=db_id).update(**updates)

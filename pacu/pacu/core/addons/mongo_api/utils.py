from datetime import datetime
import mongoengine as me

def mongo_to_dict(obj, exclude_fields = [], reference_fields= [], **kwargs):
    """ Converts a mongoengine document to a dict. 
    If nested documents are included in `reference_fields` it will recursivly convert the reference.
    Document class will be returned as `cls`.
    
    Args:
        obj (Document): mongoengine document
        exclude_fields (list, optional): Defaults to []. fields to exclude in dict. Even if references.
        reference_fields (list, optional): Defaults to []. fields to reference.
    
    Returns:
        [dict]: converted document
    """

    return_data = []

    if obj is None:
        return None

    if isinstance(obj, me.Document):
        return_data.append(("id",str(obj.id)))
        return_data.append(("cls",str(obj._cls.split('.')[-1])))

        for field_name in obj._fields:

            if field_name in exclude_fields:
                continue

            if field_name in ("id",):
                continue

            if field_name in reference_fields:
                dereference = False
            else:
                dereference = True

            data = obj[field_name]

            if isinstance(obj._fields[field_name], me.ListField):
                list_data = []
                for item in data:
                    list_data.append(mongo_to_python_type(item, item,
                        exclude_fields = exclude_fields,
                        reference_fields = reference_fields,
                        dereference = dereference
                        ))
                return_data.append((field_name, list_data))
            else:
                return_data.append((field_name, mongo_to_python_type(obj._fields[field_name], data,
                    exclude_fields = exclude_fields,
                    reference_fields = reference_fields,
                    dereference = dereference
                    )))

    return dict(return_data)

def mongo_to_python_type(field, data, dereference= True, exclude_fields= [], reference_fields= [], **kwargs):
    """ 'mongo_to_dict' helper function. Converts mongo field to a python type.
    
    Args:
        field (mongoengine field Object): field Object
        data (any): field contents
        dereference (bool, optional): Defaults to True. whether to dereference this if `field` is appropriate type
        exclude_fields (list, optional): Defaults to []. fields to exclude in dict. Even if references.
        reference_fields (list, optional): Defaults to []. fields to reference.
    
    Returns:
        [type]: python type corresponding to field
    """

    if isinstance(field, me.DateTimeField):
        return str(data.isoformat())
    elif isinstance(field, me.ComplexDateTimeField):
        return field.to_python(data).isoformat()
    elif isinstance(field, me.StringField):
        return str(data)
    elif isinstance(field, me.FloatField):
        return float(data)
    elif isinstance(field, me.IntField):
        return int(data)
    elif isinstance(field, me.BooleanField):
        return bool(data)
    elif isinstance(field, me.DictField):
        return data    
    elif isinstance(field, me.DecimalField):
        return data

    if not dereference:
        if isinstance(field, me.ReferenceField):
            return mongo_to_dict(data, exclude_fields, reference_fields)
        elif isinstance(field, me.EmbeddedDocument):
            return mongo_to_dict(data, exclude_fields, reference_fields)
        elif isinstance(field, me.EmbeddedDocumentField):
            return mongo_to_dict(data, exclude_fields, reference_fields)
        elif isinstance(field, me.Document):
            return mongo_to_dict(data, exclude_fields, reference_fields)

    else:
        if isinstance(field, me.ReferenceField):
            return str(data.id)
        elif isinstance(field, me.EmbeddedDocument):
            return str(data.id)
        elif isinstance(field, me.EmbeddedDocumentField):
            return str(data.id)
        elif isinstance(field, me.Document):
            return str(data.id)
        
        return str(data)

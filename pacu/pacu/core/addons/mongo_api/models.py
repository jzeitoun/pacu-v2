from mongoengine import *
from datetime import datetime
from pacu.core.addons.mongo_api.utils import mongo_to_dict

class User(Document):
    """ Default user document.
    """
    username = StringField(max_legngth = 50, required=True)
    password = StringField(max_legngth = 255, required = True)
    email = EmailField(max_legngth = 255, required = True)
    first_name = StringField(max_legngth = 50, required=True)
    last_name = StringField(max_legngth = 50, required=True)
    girder_key = StringField(max_legngth = 255)
    created = DateTimeField(default=datetime.utcnow())

    meta = {'collection': 'users'}

class Project(Document):
    """ Default project document.
    """
    owner = ReferenceField('User')
    name = StringField(max_legngth=50, required=True)
    created = DateTimeField(default=datetime.utcnow())

    meta = {'collection': 'projects'}

    def to_dict(self, **kwargs):
        return mongo_to_dict(self, **kwargs)


class Experiment(Document):
    """ Default Experiment document.
    """
    owner = ReferenceField('User')
    name = StringField(max_legngth=50, required=True)
    project = ReferenceField('Project', required=True)
    created = DateTimeField(default=datetime.utcnow())

    meta = {'collection': 'experiments'}

    def to_dict(self, **kwargs):
        return mongo_to_dict(self, **kwargs)

class Workspace(Document):
    """ Default workspace document.
    """
    owner = ReferenceField('User', required=True)
    name = StringField(max_legngth = 50, required=True)
    experiment = ReferenceField('Experiment', required=True)
    created = DateTimeField(default=datetime.utcnow())
    modified = DateTimeField(default=datetime.utcnow())

    images = ListField(ReferenceField('Image'))
    overlays = ListField(GenericReferenceField())

    meta = {'collection': 'workspaces'}

    def to_dict(self, **kwargs):
        return mongo_to_dict(self, **kwargs)


class StimulusGratingTrial(EmbeddedDocument):
    """ Field to hold individual trial information from visual stimulus
    """

    type = StringField(choices=['flicker', 'blank', 'texture'])

    texture = StringField()

    orientation = FloatField()
    contrast = FloatField()
    temporal_frequency = FloatField()
    spatial_frequency = FloatField()


class Stimulus(DynamicEmbeddedDocument):
    """ Default Field to hold image behavior data
    """

    viewing_eyes = StringField(max_legngth = 5, default='both')
    meta = {'collection': 'stimuli', 'allow_inheritance': True}


class StimulusGratingTrial(EmbeddedDocument):
    """ Field to hold individual trial information from visual stimulus
    """

    type = StringField(choices=['flicker', 'blank', 'texture'])

    texture = StringField()

    orientation = FloatField()
    contrast = FloatField()
    temporal_frequency = FloatField()
    spatial_frequency = FloatField()


class StimulusGrating(Stimulus):
    """ Field to hold image behavior data from visual stimulus
    """

    # monitor config
    view_distance = FloatField()
    projection = StringField(max_length=50)
    viewport_height_cm = FloatField()
    viewport_height_px = FloatField()
    viewport_width_cm = FloatField()
    viewport_width_px = IntField()
    gamma = FloatField()

    # interface config
    handler = StringField()

    # stimulus config
    repetitions = IntField()
    textures = ListField(StringField())
    contrasts = ListField(FloatField())
    orientations = ListField(FloatField())
    temporal_frequencies = ListField(FloatField())
    spatial_frequencies = ListField(FloatField())

    stimulus_on_duration = FloatField()
    blank_duration = FloatField()
    flicker_duration = FloatField()

    # trial info
    n_trials = IntField()
    trials = ListField(EmbeddedDocumentField(StimulusGratingTrial))

    log = StringField()


class ImageMeta(DynamicEmbeddedDocument):
    """ Default metadata field for microscope information
    """

    system = StringField(max_legngth=50, required=True)


class Image(Document):
    """ Default image document.
        This will hold all info regarding an image.
    """
    owner = ReferenceField('User', required=True)
    name = StringField(max_legngth = 50, required=True)

    temp_file = StringField(max_legngth = 255)
    girder_id = StringField(max_legngth = 255)

    # sample info
    sample = StringField()
    session = IntField()
    acquisition = IntField()
    acquisition_date = DateTimeField(default=datetime.utcnow())
    hemisphere = StringField(max_legngth = 255)

    # acquisition info
    metadata = EmbeddedDocumentField(ImageMeta)
    stimulus = GenericEmbeddedDocumentField()

    meta = {'collection': 'images'}

class Overlay(Document):
    """ Default overlay document.
    """
    owner = ReferenceField('User', required=True)
    name = StringField(max_legngth = 50, required=True)
    created = DateTimeField(default=datetime.utcnow())
    modified = DateTimeField(default=datetime.utcnow())

    images = ListField(LazyReferenceField('Image'))

    meta = {'collection': 'overlays', 'allow_inheritance': True}

    def to_dict(self, **kwargs):
        return mongo_to_dict(self, **kwargs)


class TaskResult(EmbeddedDocument):

    celery_id = StringField(max_legngth = 50)


    inputs = DictField()
    params = DictField()
    output = DictField()

    meta = {'collection': 'tasks'}

class Roi(Document):
    """ Individual roi class. includes all analysis done on roi.
        rois fields should have formats:
            'coordinates': array of X x Y,
            'type': shape type,
    """

    coordinates = ListField(ListField())
    surround_offset = FloatField()
    analysis = MapField(EmbeddedDocumentField(TaskResult))

    meta = {'collection': 'rois'}



class Rois(Overlay):
    """ Overlay subclass that holds roi info
    """
    rois = MapField(ReferenceField(Roi))

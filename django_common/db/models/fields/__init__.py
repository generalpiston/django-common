import uuid

from django.db import models

# All 50 states.
STATES = (
    ("AL","AL"),
    ("AK","AK"),
    ("AZ","AZ"),
    ("AR","AR"),
    ("CA","CA"),
    ("CO","CO"),
    ("CT","CT"),
    ("DE","DE"),
    ("FL","FL"),
    ("GA","GA"),
    ("HI","HI"),
    ("ID","ID"),
    ("IL","IL"),
    ("IN","IN"),
    ("IA","IA"),
    ("KS","KS"),
    ("KY","KY"),
    ("LA","LA"),
    ("ME","ME"),
    ("MD","MD"),
    ("MA","MA"),
    ("MI","MI"),
    ("MN","MN"),
    ("MS","MS"),
    ("MO","MO"),
    ("MT","MT"),
    ("NE","NE"),
    ("NV","NV"),
    ("NH","NH"),
    ("NJ","NJ"),
    ("NM","NM"),
    ("NY","NY"),
    ("NC","NC"),
    ("ND","ND"),
    ("OH","OH"),
    ("OK","OK"),
    ("OR","OR"),
    ("PA","PA"),
    ("RI","RI"),
    ("SC","SC"),
    ("SD","SD"),
    ("TN","TN"),
    ("TX","TX"),
    ("UT","UT"),
    ("VT","VT"),
    ("VA","VA"),
    ("WA","WA"),
    ("WV","WV"),
    ("WI","WI"),
    ("WY","WY"),
)

class UUIDField(models.CharField) :
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64 )
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)
    
    def pre_save(self, model_instance, add):
        if add :
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^django_common\.db\.models\.fields\.UUIDField"])
except:
    pass
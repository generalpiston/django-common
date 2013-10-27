import re, copy
from datetime import datetime, date

from django.forms.widgets import Widget, Select, DateInput, MultiWidget, Input
from django.utils import formats
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

# Attempt to match many time formats:
# Example: "12:34:56 P.M."  matches:
# ('12', '34', ':56', '56', 'P.M.', 'P', '.', 'M', '.')
# ('12', '34', ':56', '56', 'P.M.')
# Note that the colon ":" before seconds is optional, but only if seconds are omitted
time_pattern = r'(\d\d?):(\d\d)(:(\d\d))? *((a{1}|A{1}|p{1}|P{1})(\.)?(m{1}|M{1})(\.)?)?$'

RE_TIME = re.compile(time_pattern)
# The following are just more readable ways to access re.matched groups:
HOURS = 0
MINUTES = 1
SECONDS = 3
MERIDIEM = 4

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

class SplitSelectDateWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    none_value = (0, '---')
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            this_year = date.today().year
            self.years = range(this_year, this_year+10)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        
        day_choices = [(i, i) for i in range(1, 32)]
        if not (self.required and value):
            day_choices.insert(0, self.none_value)
        local_attrs = self.build_attrs(id=self.day_field % id_)
        
        s = Select(choices=day_choices)
        select_html = s.render(self.day_field % name, day_val, local_attrs)
        output.append(select_html)
            
        month_choices = MONTHS.items()
        if not (self.required and value):
            month_choices.append(self.none_value)
        month_choices.sort()
        local_attrs['id'] = self.month_field % id_
        
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        if not (self.required and value):
            year_choices.insert(0, self.none_value)
        local_attrs['id'] = self.year_field % id_
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if y == m == d == "0":
            return None
        if y and m and d:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)

class SelectTimeWidget(Widget):
    """
    A widget that has one select box to select time.
    Allows form to show as 24hr: <hour>:<minute>,
    or as 12hr: <hour>:<minute> <am|pm>
    
    Also allows user-defined increments for minutes/seconds
    """
    meridiem_field = '%s_meridiem'
    twelve_hr = False # Default to 24hr.
    has_seconds = False
    
    def __init__(self, attrs=None, hour_step=None, minute_step=30, second_step=None, seconds=False, twelve_hr=False):
        '''
        hour_step, minute_step, second_step are optional step values for
        for the range of values for the associated select element
        twelve_hr: If True, forces the output to be in 12-hr format (rather than 24-hr)
        '''
        self.attrs = attrs or {}
        
        self.has_seconds = seconds
        
        if twelve_hr:
            self.twelve_hr = True # Do 12hr (rather than 24hr)

        if hour_step and twelve_hr:
            self.hours = range(0, 12, hour_step)
        elif hour_step: # 24hr, with stepping.
            self.hours = range(0, 24, hour_step)
        elif twelve_hr: # 12hr, no stepping
            self.hours = range(0, 12)
        else: # 24hr, no stepping
            self.hours = range(0, 24)

        if minute_step:
            self.minutes = range(0, 60, minute_step)
        else:
            self.minutes = range(0, 60)

        if second_step:
            self.seconds = range(0, 60, second_step)
        else:
            self.seconds = range(0, 60)
    
    def render(self, name, value, attrs=None):
        try:
            hour_val, minute_val, second_val = value.hour, value.minute, value.second
            if self.twelve_hr:
                if hour_val >= 12:
                    meridiem_val = 'p.m.'
                else:
                    meridiem_val = 'a.m.'
            else:
                meridiem_val = None
        except AttributeError:
            hour_val = minute_val = second_val = meridiem_val = ''
            if isinstance(value, basestring):
                match = RE_TIME.match(value)
                if match:
                    time_groups = match.groups();
                    hour_val = int(time_groups[HOURS]) % 24 # force to range(0-24)
                    minute_val = int(time_groups[MINUTES])

                    if time_groups[SECONDS] is None:
                        second_val = 0
                    else:
                        second_val = int(time_groups[SECONDS])

                    # check to see if meridiem was passed in
                    if time_groups[MERIDIEM] is not None:
                        meridiem_val = time_groups[MERIDIEM]
                    else: # otherwise, set the meridiem based on the time
                        if self.twelve_hr:
                            if hour_val >= 12:
                                meridiem_val = 'p.m.'
                            else:
                                meridiem_val = 'a.m.'
                        else:
                            meridiem_val = None

        if self.twelve_hr and hour_val:
            hour_val = hour_val % 12

        output = []
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        # NOTE: for times to get displayed correctly, the values MUST be converted to unicode
        # When Select builds a list of options, it checks against Unicode values
        if hour_val != '':
            hour_val = "%.2d" % hour_val
        if minute_val != '':
            minute_val = "%.2d" % minute_val
        if second_val != '':
            second_val = "%.2d" % second_val
        val = None
        if self.has_seconds:
            val = u"%.2s:%.2s:%.2s" % (hour_val, minute_val, second_val)
        else:
            val = u"%.2s:%.2s" % (hour_val, minute_val)
        
        choices = []
        for hour in self.hours:
            for minute in self.minutes:
                if self.has_seconds:
                    for second in self.seconds:
                        choices.append((u"%.2d:%.2d:%.2d" % (hour, minute, second), u"%.2d:%.2d:%.2d" % (hour, minute, second)))
                else:
                    choices.append((u"%.2d:%.2d" % (hour, minute), u"%.2d:%.2d" % (hour, minute)))
        local_attrs = self.build_attrs(id=id_)
        select_html = Select(choices=choices).render(name, val, local_attrs)
        output.append(select_html)

        if self.twelve_hr:
            #  If we were given an initial value, make sure the correct meridiem get's selected.
            if meridiem_val and meridiem_val.startswith('p'):
                meridiem_choices = [('p.m.', 'p.m.'), ('a.m.', 'a.m.'), ('', '--')]
            else:
                meridiem_choices = [('', '--'), ('a.m.', 'a.m.'), ('p.m.', 'p.m.')]

            local_attrs['id'] = self.meridiem_field % id_
            select_html = Select(choices=meridiem_choices).render(self.meridiem_field % name, meridiem_val, local_attrs)
            output.append(select_html)

        selects_html = u'\n'.join(output)

        return mark_safe('<div class="%s">%s</div>') % (self.attrs.get('class', 'friendly_time_widget'), selects_html)
    
    def value_from_datadict(self, data, files, name):
        meridiem = data.get(self.meridiem_field % name)
        t = data.get(name) # time
        h = t[0:2]
        m = t[3:5]
        s = "00"
        if len(t) > 7:
            s = t[6:7]
        if meridiem is not None:
            if meridiem.lower().startswith('p'):
                h = (int(h) + 12) % 24
        if (int(h) == 0 or h) and m is not None and s is not None:
            return '%s:%s:%s' % (h, m, s)
        return t

class SplitSelectTimeWidget(Widget):
    """
    A Widget that splits time input into <select> elements.
    Allows form to show as 24hr: <hour>:<minute>,
    or as 12hr: <hour>:<minute> <am|pm> 

    Also allows user-defined increments for minutes/seconds
    """
    hour_field = '%s_hour'
    minute_field = '%s_minute'
    second_field = '%s_second'
    meridiem_field = '%s_meridiem'
    twelve_hr = False # Default to 24hr.
    has_seconds = False

    def __init__(self, attrs=None, hour_step=None, minute_step=30, second_step=None, seconds=False, twelve_hr=False):
        '''
        hour_step, minute_step, second_step are optional step values for
        for the range of values for the associated select element
        twelve_hr: If True, forces the output to be in 12-hr format (rather than 24-hr)
        '''
        self.attrs = attrs or {}
        
        self.has_seconds = seconds
        
        if twelve_hr:
            self.twelve_hr = True # Do 12hr (rather than 24hr)

        if hour_step and twelve_hr:
            self.hours = range(1, 13, hour_step)
        elif hour_step: # 24hr, with stepping.
            self.hours = range(0, 24, hour_step)
        elif twelve_hr: # 12hr, no stepping
            self.hours = range(1, 13)
        else: # 24hr, no stepping
            self.hours = range(0, 24)

        if minute_step:
            self.minutes = range(0, 60, minute_step)
        else:
            self.minutes = range(0, 60)

        if second_step:
            self.seconds = range(0, 60, second_step)
        else:
            self.seconds = range(0, 60)

    def render(self, name, value, attrs=None):
        try: # try to get time values from a datetime.time object (value)
            hour_val, minute_val, second_val = value.hour, value.minute, value.second
            if self.twelve_hr:
                if hour_val >= 12:
                    meridiem_val = 'p.m.'
                else:
                    meridiem_val = 'a.m.'
            else:
                meridiem_val = None
        except AttributeError:
            hour_val = minute_val = second_val = meridiem_val = ''
            if isinstance(value, basestring):
                match = RE_TIME.match(value)
                if match:
                    time_groups = match.groups();
                    hour_val = int(time_groups[HOURS]) % 24 # force to range(0-24)
                    minute_val = int(time_groups[MINUTES])

                    if time_groups[SECONDS] is None:
                        second_val = 0
                    else:
                        second_val = int(time_groups[SECONDS])

                    # check to see if meridiem was passed in
                    if time_groups[MERIDIEM] is not None:
                        meridiem_val = time_groups[MERIDIEM]
                    else: # otherwise, set the meridiem based on the time
                        if self.twelve_hr:
                            if hour_val >= 12:
                                meridiem_val = 'p.m.'
                            else:
                                meridiem_val = 'a.m.'
                        else:
                            meridiem_val = None

        if self.twelve_hr:
            # Modify the hour value appopriately for 12-hour clocks.
            if hour_val > 12 and hour_val < 24:
                hour_val = hour_val % 12
            elif hour_val == 0:
                hour_val = 12

        output = []
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        # NOTE: for times to get displayed correctly, the values MUST be converted to unicode
        # When Select builds a list of options, it checks against Unicode values
        if hour_val != '':
            hour_val = u"%.2d" % hour_val
        if minute_val != '':
            minute_val = u"%.2d" % minute_val
        if second_val != '':
            second_val = u"%.2d" % second_val

        hour_choices = [("%.2d" % i, "%.2d" % i) for i in self.hours]
        hour_choices[0:0] = [('', '--')]
        local_attrs = self.build_attrs(id=self.hour_field % id_)
        select_html = Select(choices=hour_choices).render(self.hour_field % name, hour_val, local_attrs)
        output.append(select_html)

        minute_choices = [("%.2d" % i, "%.2d" % i) for i in self.minutes]
        minute_choices[0:0] = [('', '--')]
        local_attrs['id'] = self.minute_field % id_
        select_html = Select(choices=minute_choices).render(self.minute_field % name, minute_val, local_attrs)
        output.append(select_html)
        
        if self.has_seconds:
            second_choices = [("%.2d" % i, "%.2d" % i) for i in self.seconds]
            second_choices[0:0] = [('', '--')]
            local_attrs['id'] = self.second_field % id_
            select_html = Select(choices=second_choices).render(self.second_field % name, second_val, local_attrs)
            output.append(select_html)

        if self.twelve_hr:
            #  If we were given an initial value, make sure the correct meridiem get's selected.
            if meridiem_val and meridiem_val.startswith('p'):
                meridiem_choices = [('p.m.', 'p.m.'), ('a.m.', 'a.m.'), ('', '--')]
            else:
                meridiem_choices = [('', '--'), ('a.m.', 'a.m.'), ('p.m.', 'p.m.')]

            local_attrs['id'] = local_attrs['id'] = self.meridiem_field % id_
            select_html = Select(choices=meridiem_choices).render(self.meridiem_field % name, meridiem_val, local_attrs)
            output.append(select_html)

        selects_html = u'\n'.join(output)

        return mark_safe('<div class="friendly_time_widget">%s</div>') % (selects_html)

    def id_for_label(self, id_):
        return '%s_hour' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        meridiem = data.get(self.meridiem_field % name)
        h = data.get(self.hour_field % name, "00") # hour
        m = data.get(self.minute_field % name, "00") # minute
        s = data.get(self.second_field % name, "00") # second
        if any(falsy in (h, m) for falsy in ('', None)):
            return None
        #NOTE: if meridiem IS None, assume 24-hr
        if meridiem is not None:
            if meridiem.lower().startswith('p') and int(h) != 12:
                h = (int(h) + 12) % 24
            elif meridiem.lower().startswith('a') and int(h) == 12:
                h = 0
        if (int(h) == 0 or h) and m is not None and s is not None:
            return '%s:%s:%s' % (h, m, s)
        return data.get(name, None)

class FriendlySplitDateTimeWidget(MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes
    and uses a better time selector
    """
    date_format = formats.get_format('DATE_INPUT_FORMATS')[0]
    time_format = formats.get_format('TIME_INPUT_FORMATS')[0]

    def __init__(self, attrs=None, date_format=None, time_format=None, twelve_hr=True):
        if date_format:
            self.date_format = date_format
        if time_format:
            self.time_format = time_format
        widgets = (SplitSelectDateWidget(attrs=attrs), SplitSelectTimeWidget(attrs=attrs, twelve_hr=twelve_hr))
        super(FriendlySplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, basestring):
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

class FriendlyDateTimeWidget(MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes
    and uses a better time selector
    """
    date_format = formats.get_format('DATE_INPUT_FORMATS')[0]
    time_format = formats.get_format('TIME_INPUT_FORMATS')[0]

    def __init__(self, attrs=None, date_format=None, time_format=None, twelve_hr=True):
        if date_format:
            self.date_format = date_format
        if time_format:
            self.time_format = time_format
        if attrs is None:
            attrs = {}
        date_attrs = copy.deepcopy(attrs)
        date_attrs['class'] = 'date'
        time_attrs = copy.deepcopy(attrs)
        time_attrs['class'] = 'time'
        widgets = (DateInput(attrs=date_attrs), SelectTimeWidget(attrs=time_attrs, twelve_hr=twelve_hr))
        super(FriendlyDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, basestring):
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

class USPhoneNumberWidget(Input):
    """
    A Widget that selects country code for phone number by locale:
    """
    input_type = 'phone'

    def render(self, name, value, attrs=None):
        """
        Removes international representation
        """
        return super(USPhoneNumberWidget, self).render(value[2:], attrs)

    def value_from_datadict(self, data, files, name):
        """
        Adds locale specific international representation
        """
        value = super(USPhoneNumberWidget, self).value_from_datadict(data, files, name)
        return value and '+1%s' % value or None

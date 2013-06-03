from django import template
from django.template import NodeList
 
register = template.Library()
 
class SetVarNode(template.Node):
 
    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value
 
    def render(self, context):
        value = ""
        if isinstance(self.var_value, NodeList):
            value = self.var_value.render(context)
        else:
            try:
                value = template.Variable(self.var_value).resolve(context)
            except template.VariableDoesNotExist:
                pass
        context[self.var_name] = value
        return u""
 
def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) == 4:
        return SetVarNode(parts[1], parts[3])
    elif len(parts) == 2:
        nodelist = parser.parse(('endset',))
        parser.delete_first_token()
        return SetVarNode(parts[1], nodelist)
    else:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %} or {% set <var_name> %}<var_value>{% endset %}")
 
register.tag('set', set_var)
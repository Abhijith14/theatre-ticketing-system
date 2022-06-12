from django import template
from movie.models import Movie_Time

register = template.Library()

@register.filter(name='screen_id')
def get_screen_id(str_):
    screen_obj = Movie_Time.objects.filter(screen=str_)[0].screen_id
    return screen_obj


@register.filter(name='strtolist')
def conv_str_list(str_, id):
    str_ = eval(str_)
    return str_[id-1]

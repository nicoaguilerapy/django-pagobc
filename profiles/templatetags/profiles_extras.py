from profiles.models import Profile
from django import template

register = template.Library()

@register.simple_tag
def get_profile(request):
    try:
        return Profile.objects.get(user = request.user)
    except Exception:
        return False
    
@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 
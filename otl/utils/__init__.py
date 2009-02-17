# encoding: utf-8
from django.http import HttpResponse
from django.template import RequestContext, loader

# I've made this for old Django versions, but actually we don't need this anymore.
def render_page(request, template_name, args):
	t = loader.get_template(template_name)
	c = RequestContext(request, args)
	return HttpResponse(t.render(c))

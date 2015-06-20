from django.conf.urls import *

from django.views.generic import TemplateView

from directoalartista.apps.plancontrol import views as PlanControlViews


# /upgradeplan
urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='upgrade_plan.html'), name='upgradeplan'),
    url(r'^(?P<plan>[-\w]+)/$', PlanControlViews.contract_plan,
        name='upgrade_plan'
    ),
    url(r'^4/completed/$', PlanControlViews.contract_free, name='freecompleted')
)

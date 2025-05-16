from django.shortcuts import render
from properties.models import Logement # Import Logement model
from accounts.models import CustomUser # Import CustomUser to check type

def index(request):
    context = {}
    if request.user.is_authenticated and request.user.type == CustomUser.UserType.AGENT:
        # Agent is logged in, fetch their properties
        agent_properties = Logement.objects.filter(agent=request.user).order_by('-date_creation')[:5] # Show recent 5 for dashboard
        context['agent_properties'] = agent_properties
        context['is_agent_dashboard'] = True
        # Render a specific dashboard or use the main index template with agent-specific context
        # return render(request, 'dashboard/agent_dashboard.html', context)
    else:
        # Regular public index page, maybe show some featured properties
        featured_properties = Logement.objects.filter(statut=Logement.StatutLogement.PUBLIE).order_by('?')[:6] # Show 6 random published
        context['featured_properties'] = featured_properties
        context['is_agent_dashboard'] = False

    return render(request, 'index.html', context)


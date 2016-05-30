import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic

from .forms import *
from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required

# view for homepage - index of questions & results
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
    	return Question.objects.all().order_by('-pub_date')

# view for question detail
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_context_data(self, **kwargs):
        ctx = super(DetailView, self).get_context_data(**kwargs)
        ctx['students'] = Student.objects.all()
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# view for results detail
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

# view for submission confirmation
class ConfirmationView(generic.DetailView):
    model = Question
    template_name = 'polls/confirmation.html'

# function to process student submission
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # make Response object to store data
    response = Response(question=question, student=Student.objects.get(student_name=request.POST['name']), timestamp=timezone.now())
    response.save()
    d = response.dictionary_set.create(name = response.student.student_name + " Preferences")

    # find ranking student gave for each item under the question
    item_num = 1
    for item in question.item_set.all():
        try:
            selected_choice = request.POST["item" + str(item_num)]
        except:
            # set value to lowest possible rank
            d[item] = question.item_set.all().count()
        else:
            # add pref to response dict
            d[item] = int(selected_choice)
        d.save()
        item_num += 1
    return HttpResponseRedirect(reverse('polls:confirmation', args=(question.id,)))



def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)
    
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False
    
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
 
        
        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            
            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            

            # Update our variable to tell the template registration was successful.
            registered = True
        
        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        #else    print (user_form.errors)

# Not a HTTP POST, so we render our form using two ModelForm instances.
# These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    # Render the template depending on the context.
    return render_to_response(
                              'polls/register.html',
                              {'user_form': user_form, 'registered': registered},
                              context)



def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']
        
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/polls/')
                # An inactive account was used - no logging in!
            return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print ("Invalid login details")
            return HttpResponse("Invalid login details supplied.")

# The request is not a HTTP POST, so display the login form.
# This scenario would most likely be a HTTP GET.
    else:
    # No context variables to pass to the template system, hence the
    # blank dictionary object...
        return render_to_response('polls/login.html', {}, context)


def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
    
        return HttpResponse("You are not logged in.")

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")



@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    
    # Take the user back to the homepage.
    return HttpResponseRedirect('/polls/')

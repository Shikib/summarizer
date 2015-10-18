from itertools import islice
from django.shortcuts import  get_object_or_404, render
# from django.http import HttpResponse
# from django.template import RequestContext, loader
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from .forms import UserForm, UserProfileForm, TopicForm

from .models import Topic, UserProfile
from .bing_search import run_query
from newspaper import Article
import random

# from alchemyapi import AlchemyAPI
# alchemyapi = AlchemyAPI()

import requests

MAX_ARTICLES = 25
KEY = '745df69626f8ab2cdcc2c783f2cf5038:18:73241801'

# Create your views here.

def index(request):
	latest_topic_list = Topic.objects.order_by('-title')

	context = {'latest_topic_list': latest_topic_list}
	return render(request, 'summarizer/index.html', context)

def get_keywords(topic):
    plcontinue = None
    cont = True
    keywords = []

    try:
        while cont:
            r = requests.get("https://en.wikipedia.org/w/api.php?action=query&prop=links&format=json&titles=" + topic + \
                    "&pllimit=500&redirects" + (("&plcontinue=" + plcontinue) if plcontinue else ""))

            json = r.json()

            for link in next(iter(json["query"]["pages"].values()))["links"]:
                keywords.append(link["title"])

            cont = "continue" in json
            plcontinue = json["continue"]["plcontinue"] if "continue" in json else None

        return keywords
    except:
        return []

def get_topics(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TopicForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            topic = form.cleaned_data['topic']

            keywords = get_keywords(topic)
            rand_keywords = random.sample(keywords, min(10, len(keywords)))
            graph = { }

            for curr_node in rand_keywords:
                graph[curr_node] = []
                for curr_neighbor in get_keywords(curr_node):
                    if curr_neighbor in rand_keywords:
                        graph[curr_node].append(curr_neighbor)

            sorted_keys = sorted(graph, key=lambda x : len(graph[x]), reverse=True)

            final_keywords = list(islice(sorted_keys, 5))
            print(final_keywords)    

            result_list = []

            for word in final_keywords:
                word = word.replace (" ", "+")
                r = requests.get('http://api.nytimes.com/svc/search/v2/articlesearch.json?q='+ word + '&fl=web_url&api-key=' + KEY)
                json = r.json()
                for i in json["response"]["docs"]:
                    result_list.append(i['web_url'])

            # result_list = []


            # for word in rand_keywords:
            #     word = word.replace (" ", "+")
                
            #     # r = requests.get('http://api.nytimes.com/svc/search/v2/articlesearch.json?q='+ word + '&fl=web_url&api-key=' + KEY)
            #     r = requests.get('http://api.nytimes.com/svc/search/v2/articlesearch.json?fq=body:'+ word + '&fl=web_url&api-key=' + KEY)
            #     json = r.json()
            #     for i in json["response"]["docs"]:
            #         url = i['web_url']
            #         a = Article(url)
            #         a.download()
            #         a.parse()
            #         print (a.text, "\n")
            #         print ("================= \n ================= \n")
            #         result_list.append(url)

            for word in rand_keywords:
                links = run_query(word)
                for i in links:
                    url = i["link"]
                    a = Article(url)
                    a.download()
                    a.parse()
                    print (a.text, "\n")
                    print ("================= \n================= \n")

                result_list += links

            return render(request, 'summarizer/index.html', {'result_list': result_list})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TopicForm()

    return render(request, 'name.html', {'form': form})

@login_required(login_url='/summarizer/login')
def subscriptions(request):
	user = request.user
	userprofile = UserProfile.objects.get(user=user)
	subscription_list = userprofile.topic_set.all()
	# template = loader.get_template('dubhacks/index.html')
	# context = RequestContext(request, {
 #        'latest_topic_list': latest_topic_list,
 #    })
	# return HttpResponse(template.render(context))
	# context = {'subscription_list': subscription_list}
	return render(request, 'summarizer/subscriptions.html', {'subscription_list': subscription_list})

def detail(request, topic_id):
	try:
		topic = Topic.objects.get(pk=topic_id)
	except Topic.DoesNotExist:
		raise Http404("Topic does not exist")
	return render(request, 'summarizer/detail.html', {'topic': topic})


def register(request):
    # Like before, get the request's context.
    # context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            # if 'picture' in request.FILES:
            #     profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print (user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request, 'summarizer/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    # Like before, obtain the context for the user's request.
    # context = RequestContext(request)

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
                return HttpResponseRedirect('/summarizer/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            # print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'summarizer/login.html', {})


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required(login_url='/summarizer/login')
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/summarizer/')

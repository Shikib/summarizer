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
from .twit_search import get_tweets
from newspaper import Article
import random
import summarizer.data
import summarizer.sim
import re

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

def get_topics(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # ceate a form instance and populate it with data from the request:
        form = TopicForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            topic = form.cleaned_data['topic']
            print(topic)
            print("dfq")
            keywords = summarizer.data.get_keywords(topic)
            print(keywords)

            """
            best_words = summarizer.data.best_keywords(keywords)
            keyword_scores = summarizer.data.keyword_scores(topic, best_words)
            urls = summarizer.data.get_urls(best_words)

            print('got urls!')
            for link in urls:
                url = link['link']
                # try:
                print("tring url", url)
                a = Article(url)
                a.download()
                a.parse()
                text = a.text
                lines = [t.strip() for t in re.split("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text.replace("\n", " "))]
                print("starting summary")
                summary = summarizer.sim.summarize(lines, a.title, keyword_scores, 3) 
                print (summary, '\n')
                print ("==================\n")
                # except:
                #     print ("exception")
                #     pass
                """


            #### NYT api call ####
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

            twit_results = get_tweets(topic)
            # result_list = urls
            result_list = [] # temp

            return render(request, 'summarizer/index.html', \
                    { 'twitter_results': twit_results if len(twit_results) > 0 else None,
                      'result_list': result_list if len(result_list) > 0 else None,
                      'any': len(result_list) + len(twit_results) > 0
                      })


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

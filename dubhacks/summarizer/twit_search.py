import base64
import json
import sys

from urllib.request import urlopen, Request
from urllib.error import HTTPError


API_ENDPOINT = 'https://api.twitter.com'
API_VERSION = '1.1'
REQUEST_TOKEN_URL = '%s/oauth2/token' % API_ENDPOINT
REQUEST_RATE_LIMIT = '%s/%s/application/rate_limit_status.json' % \
                     (API_ENDPOINT, API_VERSION)

class ClientException(Exception):
    pass

class Client(object):
    """This class implements the Twitter's Application-only authentication."""

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = ''

    def request(self, url):
        """Send an authenticated request to the Twitter API."""
        if not self.access_token:
            self.access_token = self._get_access_token()

        request = Request(url)
        request.add_header('Authorization', 'Bearer %s' % self.access_token)
        try:
            response = urlopen(request)
        except HTTPError:
            raise ClientException

        raw_data = response.read().decode('utf-8')
        data = json.loads(raw_data)
        return data

    def rate_limit_status(self, resource=''):
        """Returns a dict of rate limits by resource."""
        response = self.request(REQUEST_RATE_LIMIT)
        if resource:
            resource_family = resource.split('/')[1]
            return response['resources'][resource_family][resource]
        return response

    def _get_access_token(self):
        """Obtain a bearer token."""
        bearer_token = '%s:%s' % (self.consumer_key, self.consumer_secret)
        encoded_bearer_token = base64.b64encode(bearer_token.encode('ascii'))
        request = Request(REQUEST_TOKEN_URL)
        request.add_header('Content-Type',
                           'application/x-www-form-urlencoded;charset=UTF-8')
        request.add_header('Authorization',
                           'Basic %s' % encoded_bearer_token.decode('utf-8'))

        request_data = 'grant_type=client_credentials'.encode('ascii')
        if sys.version_info < (3,4):
            request.add_data(request_data)
        else:
            request.data = request_data

        response = urlopen(request)
        raw_data = response.read().decode('utf-8')
        data = json.loads(raw_data)
        return data['access_token']

def get_tweets(topic):
    client = Client("HbcrOnYMpYrcTmrgFqZeQ1c5N", "QfVQlILJe8q8BJEociUmOSPXSabEQIsiu2crR4JKoxs1CMsrh2")
    resource_url = "https://api.twitter.com/1.1/search/tweets.json?q=" + urllib.quote_plus(topic) + "%20-filter:retweets&src=typd&count=100"
    tweet = client.request(resource_url)

    sort = sorted(tweet["statuses"], key=lambda x: x["favorite_count"] + x["retweet_count"], reverse=True)
    tweets = []

    for i in sort[:min(len(sort), 5)]:
        tweets.append("https://twitter.com/" + i["user"]["screen_name"] + "/status/" + str(i["id"]))

    return tweets

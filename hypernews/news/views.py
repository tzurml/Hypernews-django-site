from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views.generic.base import TemplateView
from django.views import View
from django.conf import settings
from django.forms import Form, CharField
import json
import collections
#-------------------- MACRO's & global -----------------------

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


#-------------------- functions -----------------------------

'''
    get title and text and create & return a dict
    for an article object
'''
def add_article_to_json(title,text):
    created = datetime.now().strftime(DATE_FORMAT)
    link_list = set()
    with open(settings.NEWS_JSON_PATH, 'r') as f:
        data = json.load(f)
        for x in data:
            link_list.add(x["link"])
        link = 1
        while(link in link_list): link += 1
        str_to_add = {"created": created, "text": text, "title": title, "link": str(link)}
    return str_to_add

#---------------------- classes ----------------------------


'''
Article page has a unique link. In our case, the link 
identifier is a number.

and the page represent the data of the article
'''
class Article(TemplateView):
    template_name = 'news/news.html'

    def get_context_data(self, **kwargs):
            with open(settings.NEWS_JSON_PATH, 'r') as f:
                data = json.load(f)
                for x in data:
                    if x['link'] == kwargs['post_id']:
                        return x
                raise Http404


class ComingSoon(View):
    def get(self, request, *args, **kwargs):
        return redirect('/news/')

'''
the main page of the news website
show information about your news: the publication date, the title, 
and the link to its page.
Group them by date into unordered list
'''
class MainPage(View):

    class CreateForm(Form):
        q = CharField(label='Search', min_length=1, max_length=20)

    def get(self, request, *args, **kwargs):
        data =dict()
        with open(settings.NEWS_JSON_PATH, 'r') as f:
            news_from_json = json.load(f)
            query = request.GET.get('q')
            if query is not None:
                news_from_json = [x for x in news_from_json if query in x['title']]
                if len(news_from_json) >= 1:
                    data = {'count': len(news_from_json), 'q': query}
                else:
                    return render(request, 'news/main.html', context={'q': query, 'form': self.CreateForm})
        return render(request,'news/main.html',context={'data': data, 'news': news_from_json, 'form': self.CreateForm})


'''
add a new article to our site
redirect to main
'''
class Create(View):

    def get(self, request, *args, **kwargs):
        return render(request,'news/create.html')

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')
        text = request.POST.get('text')
        new_str = add_article_to_json(title,text)
        with open(settings.NEWS_JSON_PATH, 'r+') as f:
            file = json.load(f)
            file.append(new_str)
            f.seek(0)
            json.dump(file, f)
        return redirect('/news/')




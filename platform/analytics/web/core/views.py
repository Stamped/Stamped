# Create your views here.

import Globals

import keys.aws, logs, utils

from django.http import HttpResponse
from django.template import Context, loader
from Dashboard import Dashboard
from topStamped import getTopStamped
from datetime import *
from Enrichment import getEnrichmentStats
import Stats


from django.contrib.auth.decorators     import login_required
from logsQuery                          import logsQuery
from MongoStampedAPI                    import MongoStampedAPI
from boto.sdb.connection                import SDBConnection
from boto.exception                     import SDBResponseError
from db.mongodb.MongoStatsCollection    import MongoStatsCollection
from gevent.pool                        import Pool
from django.contrib.auth                import authenticate, login
from weeklyScore                        import weeklyScore
from django import forms
from analytics_utils import *


utils.init_db_config('peach.db3')

api = MongoStampedAPI()
stamp_collection = api._stampDB._collection
acct_collection = api._userDB._collection
entity_collection = api._entityDB._collection
todo_collection = api._todoDB._collection

conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
dash = Dashboard(api)

def index(request):
    
    today_stamps_hourly,todayStamps,yest_stamps_hourly,yestStamps,week_stamps_hourly,weekStamps,deltaStampsDay,deltaStampsWeek = dash.newStamps()

    today_accts_hourly,todayAccts,yest_accts_hourly,yestAccts,week_accts_hourly,weekAccts,deltaAcctsDay,deltaAcctsWeek = dash.newAccounts()
    
    today_users_hourly,todayUsers,yest_users_hourly,yestUsers,week_users_hourly,weekUsers,deltaUsersDay,deltaUsersWeek = dash.todaysUsers()
    
    stamp_graph = [today_stamps_hourly,yest_stamps_hourly,week_stamps_hourly]
    acct_graph = [today_accts_hourly,yest_accts_hourly,week_accts_hourly]
    users_graph = [today_users_hourly,yest_users_hourly,week_users_hourly]
    
    hours = []
    for i in range (0,24):
        hours.append(i)
    
    t = loader.get_template('../html/index.html')
    c = Context({
        'hour': est().hour,
        'minute': est().minute,
        'todayStamps': todayStamps,
        'yestStamps': yestStamps,
        'weekStamps': '%.2f' % weekStamps,
        'deltaStampsDay': '%.2f' % deltaStampsDay,
        'deltaStampsWeek': '%.2f' % deltaStampsWeek,
        'todayAccts': todayAccts,
        'yestAccts': yestAccts,
        'weekAccts': '%.2f' % weekAccts,
        'deltaAcctsDay': '%.2f' % deltaAcctsDay,
        'deltaAcctsWeek': '%.2f' %deltaAcctsWeek,
        'todayUsers': todayUsers,
        'yestUsers': yestUsers,
        'weekUsers': '%.2f' % weekUsers,
        'deltaUsersDay': '%.2f' % deltaUsersDay,
        'deltaUsersWeek': '%.2f' % deltaUsersWeek,
        'stamp_graph': stamp_graph,
        'acct_graph': acct_graph,
        'user_graph': users_graph,
        'hours': hours

        
    })
    return HttpResponse(t.render(c))

def enrichment(request):
    
    media_items,songs,movies,books,media_colls,shows,albums,places,percentSingle,artists,app = getEnrichmentStats(entity_collection)
    
    t = loader.get_template('../html/enrichment.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
                 'media_items': media_items,
                 'songs': songs,
                 'movies': movies,
                 'books': books,
                 'media_colls': media_colls,
                 'shows': shows,
                 'albums': albums,
                 'places': places,
                 'percentSingle': percentSingle,
                 'artists': artists,
                 'apps': app
    
    })
    return HttpResponse(t.render(c))

def latency(request):
    
    query = logsQuery()
    
    blacklist = []
    whitelist = []
    try: 
        blacklist = request.POST['blacklist'].split(',')
    except KeyError:
        try:
            whitelist = request.POST['whitelist'].split(',')
        except KeyError:
            pass
    
    is_blacklist = len(blacklist) > 0
    is_whitelist = len(whitelist) > 0
    
    latency = query.latencyReport(weekAgo(today()),now(),None,blacklist,whitelist)
        
    t = loader.get_template('../html/latency.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
                 'report': latency,
                 'blacklist': blacklist,
                 'whitelist': whitelist,
                 'is_whitelist': is_whitelist,
                 'is_blacklist': is_blacklist
    })
    return HttpResponse(t.render(c))

def segmentation(request):
    scorer = weeklyScore(api)
    
    if today().month > 1:
        monthAgo = datetime(today().year, today().month - 1, today().day)
    else:
        monthAgo = datetime(today().year - 1, 12,today(),day)
    
    
    usersW,powerW,avgW,lurkerW,dormantW,mean_scoreW = scorer.segmentationReport(weekAgo(today()),now(),False)
    usersM,powerM,avgM,lurkerM,dormantM,mean_scoreM = scorer.segmentationReport(monthAgo,now(),True)
    
    t = loader.get_template('../html/segmentation.html')
    c = Context({
                 'hour': est().hour,
                 'minute': est().minute,
                 'monthAgo': monthAgo,
                 'weekAgo': weekAgo(today()),
                 'usersW': '%s' % usersW,
                 'powerW': '%.2f' % powerW,
                 'avgW': '%.2f' % avgW,
                 'lurkerW': '%.2f' % lurkerW,
                 'dormantW': '%.2f' % dormantW,
                 'meanW': '%.2f' % mean_scoreW,
                 'usersM': '%s' % usersM,
                 'powerM': '%.2f' % powerM,
                 'avgM': '%.2f' % avgM,
                 'lurkerM': '%.2f' % lurkerM,
                 'dormantM': '%.2f' % dormantM,
                 'meanM': '%.2f' % mean_scoreM,

    })
    return HttpResponse(t.render(c))

def trending(request):
    
    class trendForm(forms.Form):
        quantities =[("25","Top 25"),("10","Top 10"),("50","Top 50"),("100","Top 100"),("200","Top 200")]
        stats = [("stamped","Stamped"),("todod","Todo'd")]
        scopes = [("today","Today"),("week","This Week"),("month","This Month"),("all-time","All Time")]
        verticals = [("all","All Entities"),("restaurant,bar,cafe","Restaurants & Bars"),("book","Books"),("track,album,artist","Music"),("tv,movie","Film & TV"),('app',"Software")]
        quantity = forms.CharField(max_length=30,
                widget=forms.Select(choices=quantities))
        stat = forms.CharField(max_length=30,
                widget=forms.Select(choices=stats))
        scope = forms.CharField(max_length=30,
                widget=forms.Select(choices=scopes))
        vertical = forms.CharField(max_length=30,
                widget=forms.Select(choices=verticals))
 
 
    if today().month > 1:
        monthAgo = datetime(today().year, today().month - 1, today().day)
    else:
        monthAgo = datetime(today().year - 1, 12,today(),day)
    
    bgn = today().isoformat()  
    kinds=None
    quant = 25
    scope = 'today'       
    if request.method == 'POST': 
        form = trendForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            stat = form.cleaned_data['stat']
            scope = form.cleaned_data['scope']
            kinds = form.cleaned_data['vertical']
            quant = form.cleaned_data['quantity']
            
            if stat == 'stamped':    
                collection = stamp_collection
            elif stat == 'todod':
                collection = todo_collection
            
            print kinds
            if kinds == 'all':
                kinds = None
            
            bgns = {
                    'today': today().isoformat(),
                    'week': weekAgo(today()).isoformat(),
                    'month': monthAgo.isoformat(),
                    'all-time':v1_init().isoformat()
                    }
            quant = int(quant)
            bgn = bgns[scope]
            results = getTopStamped(kinds,bgn,collection)
            results = results[0:quant]
            
    
    else: 
        form = trendForm()
        results = getTopStamped(kinds,today().isoformat(),stamp_collection)
        results = results[0:quant]
    
    t = loader.get_template('../html/trending.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
                 'monthAgo': monthAgo,
                 'weekAgo': weekAgo(today()),
                 'results': results,
                 'form': form,
                 'bgn': bgn,
                 'quantity': quant,
                 'scope': scope

    })
    return HttpResponse(t.render(c))

def custom(request):

    class inputForm(forms.Form):
        stat_choices =[("stamps","Stamps Created"),("agg_stamps","Aggregate Stamps"),("accounts","Accounts Created"),("agg_accts","Aggregate Accounts"),("users","Active Users"),("friendships","Friendships Created"),("friends","Number of Friends"),
                       ("comments","Comments Posted"),("todos","Todos Created"),("todos_c","Todos Completed"),("likes","Likes"),("entities","Entities Created"),("actions","Entity Actions")]
        stat = forms.CharField(max_length=30,
                widget=forms.Select(choices=stat_choices))
        start_date = forms.DateTimeField()
        end_date = forms.DateTimeField(required=False)
        scope = forms.CharField(max_length=10,
                widget = forms.Select(choices=[("day","By Day"),("Week","By Week"),("Month","By Month"),("total","Total")]))
        filter = forms.CharField(max_length=20,
                widget = forms.Select(choices=[("false","Overall"),("true","Per User")]))
        
   
    bgns,ends,values,base = [],[],[],[]
    if request.method == 'POST': 
        form = inputForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            stat = form.cleaned_data['stat']
            bgn = form.cleaned_data['start_date']
            scope = form.cleaned_data['scope']
            per = form.cleaned_data['filter']
            end = form.cleaned_data['end_date']
            if end is not None and end > today():
                end = today()
            stats = Stats.Stats()
            perUser = False
            if per == "true":
                perUser = True
            output = stats.query(scope, stat, bgn, end, perUser)
            bgns,ends,values,base = stats.setupGraph(output)
            
            
    else: form = inputForm()
    
    t = loader.get_template('../html/custom.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
                 'form': form,
                 'bgns': bgns,
                 'ends': ends,
                 'values': values,
                 'base': base

    })
    return HttpResponse(t.render(c))



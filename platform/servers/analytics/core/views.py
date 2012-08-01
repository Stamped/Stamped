# Create your views here.

import Globals
import keys.aws, logs, utils, time

from datetime                               import datetime,timedelta

from boto.sdb.connection                    import SDBConnection
from boto.exception                         import SDBResponseError

from gevent.pool                            import Pool

from django                                 import forms
from django.http                            import HttpResponse
from django.template                        import Context, loader
from django.contrib.auth                    import authenticate, login
from django.contrib.auth.decorators         import login_required

from servers.analytics.core                 import Stats
from servers.analytics.core.Dashboard       import Dashboard
from servers.analytics.core.topStamped      import getTopStamped
from servers.analytics.core.Enrichment      import getEnrichmentStats
from servers.analytics.core.logsQuery       import logsQuery
from servers.analytics.core.weeklyScore     import weeklyScore
from servers.analytics.core.mongoQuery      import mongoQuery
from servers.analytics.core.analytics_utils import *
from libs.ec2_utils                         import get_stack

from api.MongoStampedAPI                    import MongoStampedAPI
from api.db.mongodb.MongoStatsCollection    import MongoStatsCollection

stack_name = 'bowser'

api = MongoStampedAPI()
stamp_collection = api._stampDB._collection
acct_collection = api._userDB._collection
entity_collection = api._entityDB._collection
todo_collection = api._todoDB._collection
logsQ = logsQuery(stack_name)
dash = Dashboard(api,logsQ)



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
    
    def clock(hour):
        if hour == 0:
            return "12am"
        elif hour < 12:
            return "%sam" % hour
        elif hour == 12:
            return "12pm"
        else:
            return "%spm" % (hour - 12)
        
    times = map(clock,hours)
    
    total_stamps = stamp_collection.count()
    total_accts = acct_collection.count()
    
    t = loader.get_template('../html/index.html')
    c = Context({
        'hour': est().hour,
        'minute': est().minute,
        'stack': stack_name,
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
        'hours': hours,
        'total_stamps': total_stamps,
        'total_accts': total_accts,
        'times': times

        
    })
    return HttpResponse(t.render(c))

def enrichment(request):
    
    class enrichForm(forms.Form):
        subsets =[("media_items","Media Items"),("media_colls","Media Collections"),("places","Places"),("people","People"),("software","Software")]
        type = forms.CharField(max_length=30,
                widget=forms.Select(choices=subsets))
    
    unattempted = None
    attempted = None
    breakdown = None
    percentage = None
    if request.GET.get('type') is not None: 
        form = enrichForm(request.GET)
        if form.is_valid():
            subset = form.cleaned_data['type']
            unattempted, attempted, breakdown = getEnrichmentStats(entity_collection,subset)
            percentage = "%.2f" % (float(attempted)/(unattempted+attempted) *100)
    else:
        form = enrichForm()         
    
    t = loader.get_template('../html/enrichment.html')
    c = Context({
                 'form': form,
                 'hour': est().hour,
                 'stack': stack_name,
                 'minute': est().minute,
                 'unattempted': unattempted,
                 'attempted': attempted,
                 'percentage': percentage,
                 'breakdown': breakdown,
    
    })
    return HttpResponse(t.render(c))

def latency(request):
    
    class latencyForm(forms.Form):
        uri = forms.CharField(max_length=30)
        start_date = forms.DateTimeField()
        end_date = forms.DateTimeField(required=False)
        blacklist= forms.CharField(required=False)
        whitelist= forms.CharField(required=False)

    customResults = []
    if request.method == 'POST': 
        form = latencyForm(request.POST)
        if form.is_valid():
            uri = form.cleaned_data['uri']
            bgn = form.cleaned_data['start_date']
            end = form.cleaned_data['end_date']
            blacklist = form.cleaned_data['blacklist']
            whitelist = form.cleaned_data['whitelist']
            
            if end is None:
                end = now()
            
            customResults = query.dailyLatencyReport(bgn,end,uri,blacklist,whitelist)
            
            print customResults
            
        else: form = latencyForm()
    else: form = latencyForm()
    
    
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
    
    report = logsQ.latencyReport(dayAgo(today()),now(),None,blacklist,whitelist)
        
    t = loader.get_template('../html/latency.html')
    c = Context({
                 'hour': est().hour,
                 'minute': est().minute,
                 'stack': stack_name,
                 'report': report,
                 'blacklist': blacklist,
                 'whitelist': whitelist,
                 'is_whitelist': is_whitelist,
                 'is_blacklist': is_blacklist,
                 'form': form,
                 'customResults': customResults
    })
    return HttpResponse(t.render(c))

def stress(request):
    
    query = logsQuery(stack_name)
    
    class qpsForm(forms.Form):
        intervals =[("5","5 seconds"),("10","10 seconds"),("30","30 Seconds"),("60","60 Seconds"),("300","5 Minutes"),("600","10 Minutes")]
        windows = [("30","30 seconds"),("60","60 Seconds"),("300","5 Minutes"),("600","10 Minutes"),("1800","30 Minutes"),("3600","1 Hour")]
        window = forms.CharField(max_length=30,
                                 widget=forms.Select(choices=windows))
        interval = forms.CharField(max_length=30,
                                   widget=forms.Select(choices=intervals))

    count_report = {}
    mean_report = {}
    headers = []
    window = 0
    interval = 1
    if request.method == 'POST': 
        form = qpsForm(request.POST)
        if form.is_valid():
            window = int(form.cleaned_data['window'])
            interval = int(form.cleaned_data['interval'])
            
            count_report,mean_report = query.qpsReport(now(),interval,window)
            
            headers = map(lambda x: (now() - timedelta(seconds=(interval * x))), range(window / interval))
            
    else: form = qpsForm()
    
        
    t = loader.get_template('../html/stress.html')
    c = Context({
                 'hour': est().hour,
                 'minute': est().minute,
                 'stack': stack_name,
                 'form': form,
                 'count_results': count_report.iteritems(),
                 'mean_results': mean_report.iteritems(),
                 'n': range(0, window, interval),
                 'interval': interval,
                 'headers': headers,
    })
    return HttpResponse(t.render(c))

def segmentation(request):
    
    powerT,activeT,irregularT,dormantT = [],[],[],[]
    dates = []
    date = today()
    for i in range (0,4):
        dates.append(date)
        date = weekAgo(date)
            
    scorer = weeklyScore(api)
    
    
    for i in range (3,-1,-1):
        users,power,active,irregular,dormant,mean_score = scorer.segmentationReport(weekAgo(dates[i]),dates[i],False)
        powerT.append(power)
        activeT.append(active)
        irregularT.append(irregular)
        dormantT.append(dormant)
    
    def format(date):
        return "%s/%s" % (date.month,date.day)
            
    dates = map(format, reversed(dates))
    usersM,powerM,avgM,lurkerM,dormantM,mean_scoreM = scorer.segmentationReport(monthAgo(today()),now(),True)
    
    t = loader.get_template('../html/segmentation.html')
    c = Context({
                 'hour': est().hour,
                 'minute': est().minute,
                 'stack': stack_name,
                 'monthAgo': monthAgo(today()),
                 'weekAgo': weekAgo(today()),
                 'usersM': '%s' % usersM,
                 'powerM': '%.2f' % powerM,
                 'avgM': '%.2f' % avgM,
                 'lurkerM': '%.2f' % lurkerM,
                 'dormantM': '%.2f' % dormantM,
                 'meanM': '%.2f' % mean_scoreM,
                 'dates': dates,
                 'powerT': powerT,
                 'activeT': activeT,
                 'irregularT': irregularT,
                 'dormantT': dormantT,

    })
    return HttpResponse(t.render(c))

def trending(request):
    
    class trendForm(forms.Form):
        quantities =[("25","Top 25"),("50","Top 50"),("100","Top 100"),("200","Top 200")]
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
 
    
    bgn = today().isoformat()  
    kinds=None
    quant = 25
    scope = 'today'
    stat = 'stamped'       
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
            
            if kinds == 'all':
                kinds = None
            
            bgns = {
                    'today': today().isoformat(),
                    'week': weekAgo(today()).isoformat(),
                    'month': monthAgo(today()).isoformat(),
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
        
    mongo = mongoQuery(api)
    
    topUsers = mongo.topUsers(limit=50)
    
    t = loader.get_template('../html/trending.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
                 'stack': stack_name,
                 'monthAgo': monthAgo,
                 'weekAgo': weekAgo(today()),
                 'results': results,
                 'form': form,
                 'bgn': bgn.split('T')[0],
                 'quantity': quant,
                 'scope': scope,
                 'stat': stat,
                 'topUsers': topUsers

    })
    return HttpResponse(t.render(c))

def custom(request):

    class inputForm(forms.Form):
        stat_choices =[("stamps","Stamps Created"),("agg_stamps","Aggregate Stamps"),
                       ("accounts","Accounts Created"),("agg_accts","Aggregate Accounts"),
                       ("users","Active Users"),("friendships","Friendships Created"),
                       ("friends","Number of Friends"),("comments","Comments Posted"),
                       ("todos","Todos Created"),("todos_c","Todos Completed"),
                       ("likes","Likes"),("entities","Entities Created"),
                       ("actions","Entity Actions")]
        stat = forms.CharField(max_length=30,
                widget=forms.Select(choices=stat_choices))
        start_date = forms.DateTimeField()
        end_date = forms.DateTimeField(required=False)
        scope = forms.CharField(max_length=10,
                widget = forms.Select(choices=[("day","By Day"),("week","By Week"),("month","By Month"),("total","Total")]))
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
            
            bgn = today(bgn) + timedelta(days=1)
            if end is not None and end > now():
                end = now()
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
                 'stack': stack_name,
                 'form': form,
                 'bgns': bgns,
                 'ends': ends,
                 'values': values,
                 'base': base

    })
    return HttpResponse(t.render(c))



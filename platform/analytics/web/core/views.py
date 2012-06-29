# Create your views here.

import Globals

import keys.aws, logs, utils

from django.http import HttpResponse
from django.template import Context, loader
from Dashboard import *
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


utils.init_db_config('peach.db2')

api = MongoStampedAPI()
stamp_collection = api._stampDB._collection
acct_collection = api._userDB._collection
entity_collection = api._entityDB._collection

conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)

@login_required
def index(request):
    
    
    todayStamps,yestStamps,weekStamps,deltaStampsDay,deltaStampsWeek = newStamps()

    todayAccts,yestAccts,weekAccts,deltaAcctsDay,deltaAcctsWeek = newAccounts()
    
    todayUsrs,yestUsrs,weekUsrs,deltaUsrsDay,deltaUsrsWeek = todaysUsers()
    
    
    t = loader.get_template('../html/index.html')
    c = Context({
        'hour': now().hour,
        'minute': now().minute,
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
        'todayUsrs': todayUsrs,
        'yestUsrs': yestUsrs,
        'weekUsrs': '%.2f' % weekUsrs,
        'deltaUsrsDay': '%.2f' % deltaUsrsDay,
        'deltaUsrsWeek': '%.2f' % deltaUsrsWeek,

        
    })
    return HttpResponse(t.render(c))

@login_required
def enrichment(request):
    
    media_items,songs,movies,books,media_colls,shows,albums,places,percentSingle,artists,app = getEnrichmentStats()
    
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

@login_required
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
    
    latency = query.latencyReport(weekAgo(today()),now(),blacklist,whitelist)
        
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

@login_required
def segmentation(request):
    scorer = weeklyScore()
    
    if today().month > 1:
        monthAgo = datetime(today().year, today().month - 1, today().day)
    else:
        monthAgo = datetime(today().year - 1, 12,today(),day)
    
    
    usersW,powerW,avgW,lurkerW,dormantW,mean_scoreW = scorer.segmentationReport(weekAgo(today()),now(),False)
    usersM,powerM,avgM,lurkerM,dormantM,mean_scoreM = scorer.segmentationReport(monthAgo,now(),True)
    
    t = loader.get_template('../html/segmentation.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
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

@login_required
def trending(request):
    
    if today().month > 1:
        monthAgo = datetime(today().year, today().month - 1, today().day)
    else:
        monthAgo = datetime(today().year - 1, 12,today(),day)
    
    try:
        kinds = request.POST['vertical'].split(',')
    except KeyError:
        kinds = None
        
    if kinds == 'all':
        kinds = None
    
    todayTop = getTopStamped(kinds,today().isoformat(),stamp_collection)
    weekTop = getTopStamped(kinds,weekAgo(today()).isoformat(),stamp_collection)
    monthTop = getTopStamped(kinds,monthAgo.isoformat(),stamp_collection)
    
    t = loader.get_template('../html/trending.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
                 'monthAgo': monthAgo,
                 'weekAgo': weekAgo(today()),
                 'today': todayTop,
                 'week': weekTop,
                 'month': monthTop,

    })
    return HttpResponse(t.render(c))

@login_required
def custom(request):

    class inputForm(forms.Form):
        stat_choices =[("stamps","Stamps Created"),("accounts","Accounts Created"),("users","Active Users"),("friendships","Friendships Created")]
        stat = forms.CharField(max_length=30,
                widget=forms.Select(choices=stat_choices))
        start_date = forms.DateTimeField()
        end_date = forms.DateTimeField(required=False)
        scope = forms.CharField(max_length=10,
                widget = forms.Select(choices=[("day","By Day"),("week","By Week"),("month","By Month"),("total","Total")]))
        filter = forms.CharField(max_length=20,
                widget = forms.Select(choices=[("false","None"),("true","Per User")]))
        
   
    output = []
    if request.method == 'POST': 
        form = inputForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            stat = form.cleaned_data['stat']
            bgn = form.cleaned_data['start_date']
            scope = form.cleaned_data['scope']
            per = form.cleaned_data['filter']
            end = form.cleaned_data['end_date']

            stats = Stats.Stats()
            perUser = False
            if per == "true":
                perUser = True
            output = stats.query(scope, stat, bgn, end, perUser)
            
            
            
    else: form = inputForm()
    
    t = loader.get_template('../html/custom.html')
    c = Context({
                 'hour': now().hour,
                 'minute': now().minute,
                 'form': form,
                 'output': output,

    })
    return HttpResponse(t.render(c))



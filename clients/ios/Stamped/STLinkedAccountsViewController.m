//
//  STLinkedAccountsViewController.m
//  Stamped
//
//  Created by Landon Judkins on 6/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STLinkedAccountsViewController.h"
#import <CoreText/CoreText.h>
#import "STTextChunk.h"
#import "STChunksView.h"
#import "STRdio.h"
#import "STFacebook.h"
#import "STEvents.h"
#import "STSimpleBooleanResponse.h"
#import "STLinkedAccounts.h"
#import "STSimpleEndpointResponse.h"
#import "STActionManager.h"
#import "STSimpleAlertItem.h"
#import "STTwitter.h"
#import "STStampedAPI.h"
#import "Util.h"
#import "STSpotify.h"
#import "STPlayer.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

static const CGFloat _headerWidth = 200;
static const CGFloat _textOffset = 26;
static const CGFloat _cellHeight = 46;
static const CGFloat _headerHeight = _cellHeight;

@interface STOpenGraphCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

- (void)setupWithAlertItem:(id<STAlertItem>)item;

@property (nonatomic, readwrite, retain) UIView* title;
@property (nonatomic, readonly, retain) UIButton* button;
@property (nonatomic, readonly, retain) UIImageView* check;
@property (nonatomic, readwrite, copy) NSString* toggleID;
@property (nonatomic, readwrite, assign) BOOL locked;
@property (nonatomic, readwrite, assign) STLinkedAccountsViewController* controller;

@end


@interface STLinkedAccountsViewController () <FBRequestDelegate, UITableViewDataSource, UITableViewDelegate>

@property (nonatomic, readonly, retain) UIButton* connectToFacebook;
@property (nonatomic, readonly, retain) UIButton* connectToTwitter;
@property (nonatomic, readonly, retain) UIButton* connectToRdio;
@property (nonatomic, readonly, retain) UIButton* connectToSpotify;
@property (nonatomic, readonly, retain) UIButton* connectToNetflix;

@property (nonatomic, readonly, retain) UIButton* disconnectFromFacebook;
@property (nonatomic, readonly, retain) UIButton* disconnectFromTwitter;
@property (nonatomic, readonly, retain) UIButton* disconnectFromRdio;
@property (nonatomic, readonly, retain) UIButton* disconnectFromSpotify;
@property (nonatomic, readonly, retain) UIButton* disconnectFromNetflix;

@property (nonatomic, readonly, retain) STViewContainer* openGraphSettings;
@property (nonatomic, readonly, retain) UITableView* openGraphTable;
@property (nonatomic, readwrite, retain) NSArray<STAlertItem>* openGraphItems;
@property (nonatomic, readonly, retain) NSMutableDictionary* openGraphValues;
@property (nonatomic, readwrite, retain) STCancellation* openGraphCancellation;

@property (nonatomic, readwrite, assign) BOOL twitterPending;

@property (nonatomic, readwrite, retain) STCancellation* spotifyCancellation;

@property (nonatomic, readwrite, retain) STCancellation* netflixCancellation;
@property (nonatomic, readwrite, assign) BOOL netflixEndpointPending;

@property (nonatomic, readwrite, retain) STCancellation* linkedAccountsCancellation;
@property (nonatomic, readwrite, retain) FBRequest* meDetailsRequest;

@property (nonatomic, readwrite, assign) BOOL locked;

@end

@implementation STLinkedAccountsViewController

@synthesize connectToFacebook = _connectToFacebook;
@synthesize connectToTwitter = _connectToTwitter;
@synthesize connectToRdio = _connectToRdio;
@synthesize connectToSpotify = _connectToSpotify;
@synthesize connectToNetflix = _connectToNetflix;

@synthesize disconnectFromFacebook = _disconnectFromFacebook;
@synthesize disconnectFromTwitter = _disconnectFromTwitter;
@synthesize disconnectFromRdio = _disconnectFromRdio;
@synthesize disconnectFromSpotify = _disconnectFromSpotify;
@synthesize disconnectFromNetflix = _disconnectFromNetflix;

@synthesize openGraphSettings = _openGraphSettings;
@synthesize openGraphTable = _openGraphTable;
@synthesize openGraphItems = _openGraphItems;
@synthesize openGraphValues = _openGraphValues;
@synthesize openGraphCancellation = _openGraphCancellation;

@synthesize twitterPending = _twitterPending;

@synthesize spotifyCancellation = _spotifyCancellation;

@synthesize netflixCancellation = _netflixCancellation;
@synthesize netflixEndpointPending = _netflixEndpointPending;

@synthesize linkedAccountsCancellation = _linkedAccountsCancellation;
@synthesize meDetailsRequest = _meDetailsRequest;

@synthesize locked = _locked;

- (id)init
{
    self = [super init];
    if (self) {
        _openGraphItems = (id)[[NSArray alloc] init];
        _openGraphValues = [[NSMutableDictionary alloc] init];
        self.disableReload = YES;
    }
    return self;
}

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [STEvents removeObserver:self];
    [_connectToFacebook release];
    [_connectToTwitter release];
    [_connectToRdio release];
    [_connectToSpotify release];
    [_connectToNetflix release];
    
    [_disconnectFromFacebook release];
    [_disconnectFromTwitter release];
    [_disconnectFromRdio release];
    [_disconnectFromSpotify release];
    [_disconnectFromNetflix release];
    
    [_openGraphSettings release];
    [_openGraphTable release];
    [_openGraphItems release];
    [_openGraphValues release];
    [_openGraphCancellation release];
    
    [_spotifyCancellation cancel];
    [_spotifyCancellation release];
    
    [_netflixCancellation cancel];
    [_netflixCancellation release];
    
    [_linkedAccountsCancellation cancel];
    [_linkedAccountsCancellation release];
    _meDetailsRequest.delegate = nil;
    
    [_meDetailsRequest release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(applicationDidBecomeActive:) name:UIApplicationDidBecomeActiveNotification object:nil];
    [[STStampedAPI sharedInstance] linkedAccountsWithCallback:^(id<STLinkedAccounts> linkedAccounts, NSError *error, STCancellation *cancellation) {
        [self setupWithLinkedAccounts:linkedAccounts error:error]; 
    }];
}

- (void)setupWithLinkedAccounts:(id<STLinkedAccounts>)linkedAccounts error:(NSError*)error {
    if (linkedAccounts) {
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookAuthFinished];
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookAuthFailed];
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookCameBack];
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookLoggedOut];
        
        [STEvents addObserver:self selector:@selector(twitterAuthFinished:) event:EventTypeTwitterAuthFinished];
        [STEvents addObserver:self selector:@selector(twitterAuthFailed:) event:EventTypeTwitterAuthFailed];
        
        UIImageView* header = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"linked_accounts_greenbar"]] autorelease];
        CGRect headerFrame = header.frame;
        headerFrame.size.width = self.view.frame.size.width;
        header.frame = headerFrame;
        
        STChunk* headerStart = [STChunk chunkWithLineHeight:16 andWidth:240];
        headerStart.bottomLeft = CGPointMake(71, 24);
        STTextChunk* headerChunk1 = [[[STTextChunk alloc] initWithPrev:headerStart
                                                                  text:@"We do "
                                                                  font:[UIFont stampedFontWithSize:10]
                                                                 color:[UIColor whiteColor]] autorelease];
        STTextChunk* headerChunk2 = [[[STTextChunk alloc] initWithPrev:headerChunk1
                                                                  text:@"not"
                                                                  font:[UIFont stampedBoldFontWithSize:10]
                                                                 color:[UIColor whiteColor]] autorelease];
        STTextChunk* headerChunk3 = [[[STTextChunk alloc] initWithPrev:headerChunk2
                                                                  text:@" store or see any passwords"
                                                                  font:[UIFont stampedFontWithSize:10]
                                                                 color:[UIColor whiteColor]] autorelease];
        STChunksView* headerTextView = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObjects:
                                                                              headerChunk1,
                                                                              headerChunk2,
                                                                              headerChunk3,
                                                                              nil]] autorelease];    
        [header addSubview:headerTextView];
        UIImageView* headerLock = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"linked_accounts_lock"]] autorelease];
        [Util reframeView:headerLock withDeltas:CGRectMake(32, 12, 0, 0)];
        [header addSubview:headerLock];
        [self.scrollView appendChildView:header];
        
        UIView* socialTitle = [self headerWithTitle:@"Social"];
        [Util reframeView:socialTitle withDeltas:CGRectMake(0, -7, 0, 0)]; //compensate for header shadow
        [self.scrollView appendChildView:socialTitle];
        
        _connectToFacebook = [[self buttonWithTitle:@"Facebook"
                                           subtitle:@"Connect to Facebook"
                                             action:@selector(connectToFacebook:)
                                              image:@"welcome_facebook_btn" 
                                              color:[UIColor whiteColor]] retain];
        
        _disconnectFromFacebook = [[self buttonWithTitle:@"Facebook"
                                                subtitle:@"Disconnect from Facebook"
                                                  action:@selector(disconnectFromFacebook:)
                                                   image:@"welcome_facebook-dis_btn"
                                                   color:[UIColor stampedDarkGrayColor]] retain];
        [self wrapAndAppendViews:_connectToFacebook other:_disconnectFromFacebook];
        
        _openGraphSettings = [[STViewContainer alloc] initWithDelegate:self.scrollView andFrame:CGRectMake(0, -5, self.view.frame.size.width, 5)];
        _openGraphTable = [[UITableView alloc] initWithFrame:CGRectMake(0, 5, self.view.frame.size.width, 0)];
        _openGraphTable.backgroundColor = [UIColor clearColor];
        _openGraphTable.delegate = self;
        _openGraphTable.dataSource = self;
        _openGraphTable.separatorStyle = UITableViewCellSeparatorStyleNone;
        [_openGraphSettings addSubview:_openGraphTable];
        [_openGraphTable reloadData];
        [self.scrollView appendChildView:_openGraphSettings];
        
        if (linkedAccounts.facebook) {
            _connectToFacebook.hidden = YES;
            [self loadOpenGraphSettings];
        }
        else {
            _disconnectFromFacebook.hidden = YES;
        }
        
        _connectToTwitter = [[self buttonWithTitle:@"Twitter"
                                          subtitle:@"Connect to Twitter"
                                            action:@selector(connectToTwitter:)
                                             image:@"welcome_twitter_btn" 
                                             color:[UIColor whiteColor]] retain];
        _disconnectFromTwitter = [[self buttonWithTitle:@"Twitter"
                                               subtitle:@"Disconnect from Twitter"
                                                 action:@selector(disconnectFromTwitter:)
                                                  image:@"welcome_twitter-dis_btn" 
                                                  color:[UIColor stampedGrayColor]] retain];
        [self wrapAndAppendViews:_connectToTwitter other:_disconnectFromTwitter];
        
        if (linkedAccounts.twitter) {
            _connectToTwitter.hidden = YES;
        }
        else {
            _disconnectFromTwitter.hidden = YES;
        }
        
        UIView* socialFooter1 = [self footerWithText:@"Find friends on Stamped and share your\nactivity to Facebook and Twitter."];
        [self.scrollView appendChildView:socialFooter1];
        
        UIView* socialFooter2 = [self footerWithText:@"We will never post anything without your permission"];
        
        [Util reframeView:socialFooter2 withDeltas:CGRectMake(0, 4, 0, 19)];
        [self.scrollView appendChildView:socialFooter2];
        
        [self addDividerBar];
        
        UIView* musicTitle = [self headerWithTitle:@"Music"];
        [self.scrollView appendChildView:musicTitle];
        
        _connectToRdio = [[self buttonWithTitle:@"Rdio"
                                       subtitle:@"Connect to Rdio"
                                         action:@selector(connectToRdio:)
                                          image:@"welcome_rdio_btn" 
                                          color:[UIColor whiteColor]] retain];
        
        _disconnectFromRdio = [[self buttonWithTitle:@"Rdio"
                                            subtitle:@"Disconnect from Rdio"
                                              action:@selector(disconnectFromRdio:)
                                               image:@"welcome_rdio-dis_btn" 
                                               color:[UIColor stampedDarkGrayColor]] retain];
        [self wrapAndAppendViews:_connectToRdio other:_disconnectFromRdio];
        
        if ([STRdio sharedRdio].connected) {
            _connectToRdio.hidden = YES;
        }
        else {
            _disconnectFromRdio.hidden = YES;
        }
        
        _connectToSpotify = [[self buttonWithTitle:@"Spotify"
                                          subtitle:@"Connect to Spotify"
                                            action:@selector(connectToSpotify:)
                                             image:@"welcome_spotify_btn" 
                                             color:[UIColor whiteColor]] retain];
        _disconnectFromSpotify = [[self buttonWithTitle:@"Spotify"
                                               subtitle:@"Disconnect from Spotify"
                                                 action:@selector(disconnectFromSpotify:)
                                                  image:@"welcome_spotify-dis_btn" 
                                                  color:[UIColor stampedGrayColor]] retain];
        [self wrapAndAppendViews:_connectToSpotify other:_disconnectFromSpotify];
        
        [self updateSpotify];
        
        UIView* musicFooter = [self footerWithText:@"Access your listening history, listen to full songs in Stamped, and add songs to your playlist."];
        [Util reframeView:musicFooter withDeltas:CGRectMake(0, 0, 0, 19)];
        [self.scrollView appendChildView:musicFooter];
        
        [self addDividerBar];
        
        UIView* filmTitle = [self headerWithTitle:@"Film & TV"];
        [self.scrollView appendChildView:filmTitle];
        
        _connectToNetflix = [[self buttonWithTitle:@"Netflix"
                                          subtitle:@"Connect to Netflix"
                                            action:@selector(connectToNetflix:)
                                             image:@"welcome_netflix_btn" 
                                             color:[UIColor whiteColor]] retain];
        _disconnectFromNetflix = [[self buttonWithTitle:@"Netflix"
                                               subtitle:@"Disconnect from Netflix"
                                                 action:@selector(disconnectFromNetflix:)
                                                  image:@"welcome_netflix-dis_btn" 
                                                  color:[UIColor stampedGrayColor]] retain];
        [self wrapAndAppendViews:_connectToNetflix other:_disconnectFromNetflix];
        
        
        if (linkedAccounts.netflix) {
            _connectToNetflix.hidden = YES;
        }
        else {
            _disconnectFromNetflix.hidden = YES;
        }
        
        UIView* filmFooter = [self footerWithText:@"Access your recommendations and add stamps to your Netflix queue."];
        [Util reframeView:filmFooter withDeltas:CGRectMake(0, 0, 0, 32)];
    }
    else {
        [Util warnWithAPIError:error andBlock:^{
            [Util compareAndPopController:self animated:YES]; 
        }];
    }
}

- (void)updateSpotify {
    BOOL connected = [STSpotify sharedInstance].connected;
    self.connectToSpotify.hidden = connected;
    self.disconnectFromSpotify.hidden = !connected;
}

- (void)connectToSpotify:(id)notImportant {
    self.spotifyCancellation = [[STSpotify sharedInstance] loginWithCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
        self.spotifyCancellation = nil;
        if (error) {
            [Util warnWithAPIError:error andBlock:nil];
        }
        [self updateSpotify];
    }];
}

- (void)disconnectFromSpotify:(id)notImportant {
    self.spotifyCancellation = [[STSpotify sharedInstance] logoutWithCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
        self.spotifyCancellation = nil;
        if (error) {
            [Util warnWithAPIError:error andBlock:nil];
        }
        [self updateSpotify];
    }];
}

- (void)applicationDidBecomeActive:(NSNotification*)notification {
    if (self.netflixEndpointPending) {
        self.netflixEndpointPending = NO;
        [self checkNetflix];
    }
}

- (void)checkNetflix {
    self.netflixCancellation = [[STStampedAPI sharedInstance] linkedAccountsWithCallback:^(id<STLinkedAccounts> linkedAccounts, NSError *error, STCancellation *cancellation) {
        self.netflixCancellation = nil;
        if (linkedAccounts.netflix) {
            self.connectToNetflix.hidden = YES;
            self.disconnectFromNetflix.hidden = NO;
        }
        else {
            self.connectToNetflix.hidden = NO;
            self.disconnectFromNetflix.hidden = YES;
        }
    }];
}

- (void)connectToNetflix:(id)notImportant {
    if (!self.netflixCancellation) {
        self.netflixCancellation = [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/netflix/login.json"
                                                                                post:NO
                                                                       authenticated:YES
                                                                              params:[NSDictionary dictionary]
                                                                             mapping:[STSimpleEndpointResponse mapping]
                                                                         andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                                             self.netflixCancellation = nil;
                                                                             if (result) {
                                                                                 id<STEndpointResponse> response = result;
                                                                                 if (response.action) {
                                                                                     [[STActionManager sharedActionManager] didChooseAction:response.action withContext:[STActionContext context]];
                                                                                 }
                                                                                 else {
                                                                                     [self checkNetflix];
                                                                                 }
                                                                             }
                                                                             else {
                                                                                 [Util warnWithAPIError:error andBlock:nil];
                                                                             }
                                                                         }];
    }
}

- (void)disconnectFromNetflix:(id)notImportant {
    if (!self.netflixCancellation) {
        self.netflixCancellation = [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/netflix/remove.json"
                                                                                post:YES
                                                                       authenticated:YES
                                                                              params:[NSDictionary dictionaryWithObject:@"netflix" forKey:@"service_name"]
                                                                             mapping:[STSimpleBooleanResponse mapping]
                                                                         andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                                             self.netflixCancellation = nil;
                                                                             if (result) {
                                                                                 self.connectToNetflix.hidden = NO;
                                                                                 self.disconnectFromNetflix.hidden = YES;
                                                                             }
                                                                             else {
                                                                                 [Util warnWithAPIError:error andBlock:nil];
                                                                             }
                                                                         }];
    }
}


- (void)wrapAndAppendViews:(UIView*)view other:(UIView*)other {
    UIView* container = [[[UIView alloc] initWithFrame:CGRectMake(0,
                                                                  0,
                                                                  self.view.frame.size.width,
                                                                  CGRectGetMaxY(view.frame))] autorelease];
    [container addSubview:view];
    [container addSubview:other];
    [self.scrollView appendChildView:container];
}

- (void)reloadStampedData {
    //[self loadOpenGraphSettings];
    //[self checkNetflix];
}

- (void)twitterAuthFinished:(id)notImportant {
    self.twitterPending = NO;
    self.connectToTwitter.hidden = YES;
    self.disconnectFromTwitter.hidden = NO;
    NSMutableDictionary* params = [NSMutableDictionary dictionary];
    STTwitter* twitter = [STTwitter sharedInstance];
    NSLog(@"twitterUser:%@", twitter.twitterUser);
    [params setObject:twitter.twitterUsername forKey:@"linked_screen_name"];
    [params setObject:twitter.twitterToken forKey:@"token"];
    [params setObject:twitter.twitterTokenSecret forKey:@"secret"];
//    [params setObject:@"twitter" forKey:@"service_name"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/twitter/add.json"
                                                 post:YES
                                        authenticated:YES
                                               params:params
                                              mapping:[STSimpleBooleanResponse mapping]
                                          andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                              self.twitterPending = NO;
                                              if (result) {
                                                  
                                              }
                                              else {
                                                  self.disconnectFromTwitter.hidden = YES;
                                                  self.connectToTwitter.hidden = NO;
                                                  [Util warnWithAPIError:error andBlock:nil];
                                              }
                                          }];
}

- (void)twitterAuthFailed:(id)notImportant {
    self.twitterPending = NO;
    [Util warnWithMessage:@"Could not link to Twitter" andBlock:nil];
}

- (void)connectToTwitter:(id)notImportant {
    if (!self.twitterPending) {
        self.twitterPending = YES;
        [[STTwitter sharedInstance] auth];
    }
}

- (void)disconnectFromTwitter:(id)notImportant {
    if (!self.twitterPending) {
        self.twitterPending = YES;
        [[STStampedAPI sharedInstance] removeLinkedAccountWithService:@"twitter"
                                                          andCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
                                                              self.twitterPending = NO;
                                                              if (success) {
                                                                  self.connectToTwitter.hidden = NO;
                                                                  self.disconnectFromTwitter.hidden = YES;
                                                              }
                                                              else {
                                                                  [Util warnWithAPIError:error
                                                                                andBlock:nil];
                                                              }
                                                          }];
    }
}

- (void)facebookAuthChanged:(id)notImportant {
    if ([[STFacebook sharedInstance] isSessionValid]) {
        _connectToFacebook.hidden = YES;
        _disconnectFromFacebook.hidden = NO;
        [self loadOpenGraphSettings];
    }
    else {
        _disconnectFromFacebook.hidden = YES;
        _connectToFacebook.hidden = NO;
    }
}

- (void)connectTemp:(id)notImportant {
    [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
}

- (void)connectToFacebook:(id)notImportant {
    if (!self.locked) {
        [[STFacebook sharedInstance] auth];
    }
}

- (void)disconnectFromFacebook:(id)notImportant {
    if (!self.locked) {
        self.locked = YES;
        [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/facebook/remove.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:[NSDictionary dictionary]
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                  self.locked = NO;
                                                  if (!error) {
                                                      [[STFacebook sharedInstance] invalidate];
                                                      [self.openGraphCancellation cancel];
                                                      self.openGraphCancellation = nil;
                                                      [self.openGraphValues removeAllObjects];
                                                      self.openGraphItems = [NSArray array];
                                                  }
                                              }];
    }
}

- (void)connectToRdio:(id)notImportant {
    if (!self.locked) {
        [[STRdio sharedRdio] ensureLoginWithCompletionBlock:^{
            if ([STRdio sharedRdio].connected) {
                self.connectToRdio.hidden = YES;
                self.disconnectFromRdio.hidden = NO;
            }
            self.locked = NO;
        }];
    }
}

- (void)disconnectFromRdio:(id)notImportant {
    if (!self.locked) {
        [[STRdio sharedRdio] logout];
        self.connectToRdio.hidden = NO;
        self.disconnectFromRdio.hidden = YES;
    }
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STAlertItem> item = [self.openGraphItems objectAtIndex:indexPath.row];
    NSString* reuseID = @"OpenGraphCell";
    STOpenGraphCell* cell = [tableView dequeueReusableCellWithIdentifier:reuseID];
    if (!cell) {
        cell = [[[STOpenGraphCell alloc] initWithReuseIdentifier:reuseID] autorelease];
    }
    cell.controller = self;
    [cell setupWithAlertItem:item];
    return cell;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return self.openGraphItems.count;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return self.openGraphItems.count ? 1 : 0;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return _cellHeight;
}

- (CGFloat)tableView:(UITableView *)tableView heightForHeaderInSection:(NSInteger)section {
    return _headerHeight;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    return @"Publish to Timeline";
}

- (UIView *)tableView:(UITableView *)tableView viewForHeaderInSection:(NSInteger)section {
    UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, tableView.frame.size.width, _headerHeight)] autorelease];
    
    STChunk* titleStart = [STChunk chunkWithLineHeight:16 andWidth:200];
    STTextChunk* titleChunk = [[[STTextChunk alloc] initWithPrev:titleStart
                                                            text:[self tableView:tableView titleForHeaderInSection:section]
                                                            font:[UIFont stampedBoldFontWithSize:12]
                                                           color:[UIColor stampedDarkGrayColor]] autorelease];
    titleChunk.bottomLeft = CGPointMake(26, 26);
    STChunksView* title = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:titleChunk]] autorelease];
    [view addSubview:title];
    return view;
}

- (UIView*)footerWithText:(NSString*)text {
    STChunk* start = [STChunk chunkWithLineHeight:16 andWidth:290];
    start.bottomLeft = CGPointMake(16, 16);
    STTextChunk* textChunk = [[[STTextChunk alloc] initWithPrev:start
                                                           text:text
                                                           font:[UIFont stampedFontWithSize:12]
                                                          color:[UIColor stampedGrayColor]] autorelease];
    STChunksView* view = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:textChunk]] autorelease];
    return view;
}

- (void)addDividerBar {
    UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"two_tone_bar"]] autorelease];
    CGRect frame = imageView.frame;
    frame.size.width = self.view.frame.size.width;
    imageView.frame = frame;
    [self.scrollView appendChildView:imageView];
}

- (UIView*)headerWithTitle:(NSString*)title {
    UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, _textOffset)] autorelease];
    STChunk* start = [STChunk chunkWithLineHeight:16 andWidth:_headerWidth];
    STTextChunk* titleChunk = [[[STTextChunk alloc] initWithPrev:start
                                                            text:title
                                                            font:[UIFont stampedBoldFontWithSize:12] 
                                                           color:[UIColor stampedGrayColor]] autorelease];
    titleChunk.bottomLeft = CGPointMake(15, 26);
    STChunksView* chunksView = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:titleChunk]] autorelease];
    [view addSubview:chunksView];
    return view;
}

- (UIButton*)buttonWithTitle:(NSString*)title 
                    subtitle:(NSString*)subtitle
                      action:(SEL)action 
                       image:(NSString*)imageName 
                       color:(UIColor*)color {
    
    CGFloat originY = 10.0f;
    CGFloat originX = 10.0f;
    CGFloat width = self.view.frame.size.width-20.0f;
    
    UIButton* button = [UIButton buttonWithType:UIButtonTypeCustom];
    UIImage* image = [UIImage imageNamed:imageName];
    [button addTarget:self action:action forControlEvents:UIControlEventTouchUpInside];
    [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:image.size.width - 6.0f topCapHeight:0] forState:UIControlStateNormal];
    button.frame = CGRectMake(originX, originY, width, image.size.height);
    CATextLayer * textLayer = [self addTitle:subtitle toButton:button boldText:title color:color];
    textLayer.alignmentMode = @"left";
    CGRect frame = textLayer.frame;
    frame.origin.x = 60.0f;
    frame.origin.y -= 1.0f;
    textLayer.frame = frame;
    return button;
}


- (CATextLayer*)addTitle:(NSString*)title toButton:(UIButton*)button boldText:(NSString*)boldText color:(UIColor*)color {
    
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"HelveticaNeue" : (CFStringRef)@"Helvetica", 12, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)color.CGColor, kCTForegroundColorAttributeName, nil];
    
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)color.CGColor, kCTForegroundColorAttributeName, nil];
    
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
    if (boldText) {
        [string setAttributes:boldStyle range:[string.string rangeOfString:boldText]];
    }
    [boldStyle release];
    [defaultStyle release];
    
    CATextLayer *layer = [CATextLayer layer];
    layer.contentsScale = [[UIScreen mainScreen] scale];
    layer.frame = CGRectMake(0.0f, floorf((button.bounds.size.height - 14)/2), 180.0f, 14);
    layer.backgroundColor = [UIColor clearColor].CGColor;
    layer.alignmentMode = @"center";
    layer.string = string;
    [string release];
    [button.layer addSublayer:layer];
    return layer;
    
    
}

- (void)handleOpenGraphItems:(NSArray<STAlertItem>*)items withError:(NSError*)error {
    self.openGraphCancellation = nil;
    if (items) {
        if (self.openGraphValues.count) {
            [self consumePendingOpenGraphChanges];
        }
        else {
            self.openGraphItems = items;
        }
    }
    else {
        [Util warnWithAPIError:error andBlock:nil];
    }
}

- (void)setOpenGraphItems:(NSArray<STAlertItem> *)items {
    
    NSInteger countBefore = _openGraphItems.count;
    [_openGraphItems autorelease];
    _openGraphItems = [items retain];
    NSInteger rowDelta = items.count - countBefore;
    CGFloat heightDelta = rowDelta * _cellHeight;
    if (countBefore == 0 && rowDelta != 0) {
        heightDelta += _headerHeight;
    }
    else if (items.count == 0 && rowDelta != 0) {
        heightDelta -= _headerHeight;
    }
    CGFloat duration = .08 * (abs(heightDelta) / _cellHeight);
    CGRect frame = self.openGraphTable.frame;
    frame.size.height += heightDelta;
    [self.openGraphSettings.delegate childView:self.openGraphSettings shouldChangeHeightBy:heightDelta overDuration:duration];
    if (countBefore == 0 && rowDelta != 0) {
        self.openGraphTable.frame = frame;
        [self.openGraphTable beginUpdates];
        [self.openGraphTable insertSections:[NSIndexSet indexSetWithIndexesInRange:NSMakeRange(0, 1)] withRowAnimation:UITableViewRowAnimationFade];
        [self.openGraphTable endUpdates];
    }
    else if (items.count == 0 && rowDelta != 0) {
        [self.openGraphTable beginUpdates];
        [self.openGraphTable deleteSections:[NSIndexSet indexSetWithIndex:0] withRowAnimation:UITableViewRowAnimationFade];
        [self.openGraphTable endUpdates];
        [UIView animateWithDuration:duration animations:^{
            self.openGraphTable.frame = frame;
        }];
    }
    else {
        self.openGraphTable.frame = frame;
        [self.openGraphTable reloadData];
    }
}

- (void)consumePendingOpenGraphChanges {
    if (!self.openGraphCancellation) {
        NSMutableSet* on = [NSMutableSet set];
        NSMutableSet* off = [NSMutableSet set];
        for (NSString* tID in self.openGraphValues.allKeys) {
            NSNumber* value = [self.openGraphValues objectForKey:tID];
            if (value.boolValue) {
                [on addObject:tID];
            }
            else {
                [off addObject:tID];
            }
        }
        [self.openGraphValues removeAllObjects];
        NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                                [[on allObjects] componentsJoinedByString:@","], @"on",
                                [[off allObjects] componentsJoinedByString:@","], @"off",
                                @"facebook", @"service_name",
                                nil];
        self.openGraphCancellation = [[STRestKitLoader sharedInstance] loadWithPath:@"/account/linked/facebook/settings/update.json"
                                                                               post:YES
                                                                      authenticated:YES
                                                                             params:params
                                                                            mapping:[STSimpleAlertItem mapping]
                                                                        andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                                            [self handleOpenGraphItems:(id)results withError:error];
                                                                        }];
    }
}

- (void)loadOpenGraphSettings {
    if (!self.openGraphCancellation) {
        self.openGraphCancellation = [[STRestKitLoader sharedInstance] loadWithPath:@"/account/linked/facebook/settings/show.json"
                                                                               post:NO
                                                                      authenticated:YES
                                                                             params:[NSDictionary dictionaryWithObject:@"facebook" forKey:@"service_name"]
                                                                            mapping:[STSimpleAlertItem mapping]
                                                                        andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                                            [self handleOpenGraphItems:(id)results withError:error];
                                                                        }];
    }
}

- (void)setToggleID:(NSString*)toggleID toValue:(BOOL)value {
    NSNumber* currentValue = [self.openGraphValues objectForKey:toggleID];
    if (currentValue) {
        if (currentValue.boolValue == value) {
            return;
        }
    }
    [self.openGraphValues setObject:[NSNumber numberWithBool:value] forKey:toggleID];
    [self consumePendingOpenGraphChanges];
}


@end


@implementation STOpenGraphCell

@synthesize title = _title;
@synthesize check = _check;
@synthesize button = _button;
@synthesize toggleID = _toggleID;
@synthesize controller = _controller;
@synthesize locked = _locked;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
    if (self) {
        UIImage* buttonImage = [UIImage imageNamed:@"notifications-checkbox"];
        UIImage* checkImage = [UIImage imageNamed:@"notifications-checkmark"];
        _button = [[UIButton buttonWithType:UIButtonTypeCustom] retain];
        _button.frame = CGRectMake(240, 8, 30, 30);
        [_button setImage:buttonImage forState:UIControlStateNormal];
        [_button addTarget:self action:@selector(toggle:) forControlEvents:UIControlEventTouchUpInside];
        [self.contentView addSubview:_button];
        _check = [[UIImageView alloc] initWithImage:checkImage];
        _check.frame = _button.frame;
        [self.contentView addSubview:_check];
        self.selectionStyle = UITableViewCellSelectionStyleNone;
    }
    return self;
}

- (void)dealloc
{
    [_title release];
    [_button release];
    [_check release];
    [_toggleID release];
    [super dealloc];
}

- (void)toggle:(id)notImportant {
    if (!self.locked) {
        self.check.hidden = !self.check.hidden;
        BOOL value = !self.check.hidden;
        [self.controller setToggleID:self.toggleID toValue:value];
    }
}

- (void)setupWithAlertItem:(id<STAlertItem>)item {
    [self.title removeFromSuperview];
    self.title = nil;
    self.toggleID = nil;
    self.button.hidden = YES;
    self.locked = YES;
    STChunk* titleStart = [STChunk chunkWithLineHeight:16 andWidth:200];
    STTextChunk* titleChunk = [[[STTextChunk alloc] initWithPrev:titleStart
                                                            text:[item name]
                                                            font:[UIFont stampedFontWithSize:12]
                                                           color:[UIColor stampedGrayColor]] autorelease];
    titleChunk.bottomLeft = CGPointMake(26, 26);
    self.title = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:titleChunk]] autorelease];
    [self.contentView addSubview:self.title];
    if (item.toggles.count) {
        id<STAlertToggle> toggle = [item.toggles objectAtIndex:0];
        if (toggle.value && toggle.toggleID) {
            self.locked = NO;
            self.button.hidden = NO;
            self.check.hidden = ![toggle.value boolValue];
            self.toggleID = [toggle toggleID];      
        }
    }
}

@end


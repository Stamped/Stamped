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

static const CGFloat _headerWidth = 200;
static const CGFloat _textOffset = 26;

@interface STLinkedAccountsViewController () <FBRequestDelegate>

@property (nonatomic, readonly, retain) UIButton* connectToFacebook;
@property (nonatomic, readonly, retain) UIButton* connectToTwitter;
@property (nonatomic, readonly, retain) UIButton* connectToRdio;
@property (nonatomic, readonly, retain) UIButton* connectToSpotify;
@property (nonatomic, readonly, retain) UIButton* connectToNetflix;

@property (nonatomic, readonly, retain) UIButton* disconnectFromFacebook;
@property (nonatomic, readonly, retain) UIButton* disconnectFromRdio;
@property (nonatomic, readonly, retain) UIButton* disconnectFromNetflix;

@property (nonatomic, readwrite, assign) BOOL locked;

@end

@implementation STLinkedAccountsViewController

@synthesize connectToFacebook = _connectToFacebook;
@synthesize connectToTwitter = _connectToTwitter;
@synthesize connectToRdio = _connectToRdio;
@synthesize connectToSpotify = _connectToSpotify;
@synthesize connectToNetflix = _connectToNetflix;

@synthesize disconnectFromFacebook = _disconnectFromFacebook;
@synthesize disconnectFromRdio = _disconnectFromRdio;
@synthesize disconnectFromNetflix = _disconnectFromNetflix;

@synthesize locked = _locked;

- (id)init
{
    self = [super init];
    if (self) {
    }
    return self;
}

- (void)dealloc
{
    [STEvents removeObserver:self];
    [_connectToFacebook release];
    [_connectToTwitter release];
    [_connectToRdio release];
    [_connectToSpotify release];
    [_connectToNetflix release];
    
    [_disconnectFromFacebook release];
    [_disconnectFromRdio release];
    [_disconnectFromNetflix release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
}

- (void)setupWithLinkedAccounts:(id<STLinkedAccounts>)linkedAccounts error:(NSError*)error {
    if (linkedAccounts) {
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookAuthFinished];
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookAuthFailed];
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookCameBack];
        [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookLoggedOut];
        
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
        
        _connectToTwitter = [[self buttonWithTitle:@"Twitter"
                                          subtitle:@"Connect to Twitter"
                                            action:@selector(connectTemp:)
                                             image:@"welcome_twitter_btn" 
                                             color:[UIColor whiteColor]] retain];
        [self.scrollView appendChildView:_connectToTwitter];
        
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
                                            action:@selector(connectTemp:)
                                             image:@"welcome_spotify_btn" 
                                             color:[UIColor whiteColor]] retain];
        [self.scrollView appendChildView:_connectToSpotify];
        
        [self addDividerBar];
        
        UIView* filmTitle = [self headerWithTitle:@"Film & TV"];
        [self.scrollView appendChildView:filmTitle];
        
        _connectToNetflix = [[self buttonWithTitle:@"Netflix"
                                          subtitle:@"Connect to Netflix"
                                            action:@selector(connectTemp:)
                                             image:@"welcome_netflix_btn" 
                                             color:[UIColor whiteColor]] retain];
        _disconnectFromNetflix = [[self buttonWithTitle:@"Netflix"
                                               subtitle:@"Disconnect from Netflix"
                                                 action:@selector(connectTemp:)
                                                  image:@"welcome_netflix-dis_btn" 
                                                  color:[UIColor whiteColor]] retain];
        [self wrapAndAppendViews:_connectToNetflix other:_disconnectFromNetflix];
        
        [self addDividerBar];
        
        CGSize contentSize = self.scrollView.contentSize;
        contentSize.height += 30;
        self.scrollView.contentSize = contentSize;
        [self facebookAuthChanged:nil];
    }
    else {
        [Util warnWithAPIError:error andBlock:^{
            [Util compareAndPopController:self animated:YES]; 
        }];
    }
}

- (void)wrapAndAppendViews:(UIView*)view other:(UIView*)other {
    UIView* container = [[[UIView alloc] initWithFrame:CGRectMake(0,
                                                                  0,
                                                                  self.view.frame.size.width,
                                                                  view.frame.size.height)] autorelease];
    [container addSubview:view];
    [container addSubview:other];
    [self.scrollView appendChildView:container];
}

- (void)facebookAuthChanged:(id)notImportant {
    if ([[STFacebook sharedInstance] isSessionValid]) {
        _connectToFacebook.hidden = YES;
        _disconnectFromFacebook.hidden = NO;
        NSLog(@"facebook:%@",[[STFacebook sharedInstance] userData]);
        [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/remove.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:[NSDictionary dictionaryWithObject:@"facebook" forKey:@"service_name"]
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                  [[[STFacebook sharedInstance] facebook] requestWithGraphPath:@"me" andDelegate:self]; 
                                              }];
    }
    else {
        _disconnectFromFacebook.hidden = YES;
        _connectToFacebook.hidden = NO;
    }
}

- (void)request:(FBRequest *)request didLoad:(id)result {
    STFacebook* fb = [STFacebook sharedInstance];
    if (fb.facebook.accessToken && [result objectForKey:@"username"] && [result objectForKey:@"name"] && [result objectForKey:@"id"]) {
        NSMutableDictionary* params = [NSMutableDictionary dictionary];
        [params setObject:[result objectForKey:@"username"] forKey:@"linked_screen_name"];
        [params setObject:[result objectForKey:@"name"] forKey:@"linked_name"];
        [params setObject:[result objectForKey:@"id"] forKey:@"linked_user_id"];
        [params setObject:@"facebook" forKey:@"service_name"];
        [params setObject:fb.facebook.accessToken forKey:@"token"];
        //[params setObject:fb.facebook.expirationDate forKey:@"token_expiration"];
        [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/add.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                  
                                              }];
    }
}

- (void)connectTemp:(id)notImportant {
    [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
}

- (void)connectToFacebook:(id)notImportant {
    if (!self.locked) {
        [[STFacebook sharedInstance] auth];
        [[[STFacebook sharedInstance] facebook] requestWithGraphPath:@"me" andDelegate:self]; 
    }
}

- (void)disconnectFromFacebook:(id)notImportant {
    if (!self.locked) {
        self.locked = YES;
        [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/remove.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:[NSDictionary dictionaryWithObject:@"facebook" forKey:@"service_name"]
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                  self.locked = NO;
                                                  [[STFacebook sharedInstance] invalidate];
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

- (UIView*)footerWithText:(NSString*)text {
    STChunk* start = [STChunk chunkWithLineHeight:16 andWidth:240];
    start.bottomLeft = CGPointMake(_textOffset, 24);
    STTextChunk* textChunk = [[[STTextChunk alloc] initWithPrev:start
                                                           text:text
                                                           font:[UIFont stampedFontWithSize:12]
                                                          color:[UIColor stampedGrayColor]] autorelease];
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

@end

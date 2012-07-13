//
//  STNotificationsViewController.m
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STNotificationsViewController.h"
#import "STAlertItem.h"
#import "STStampedAPI.h"
#import "STTextChunk.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STChunksView.h"
#import "Util.h"
#import "STNavigationItem.h"

static const CGFloat _apnsOffset = 213;
static const CGFloat _emailOffset = 277;
static const CGFloat _buttonYOffset = 8;
static const CGFloat _buttonWidth = 30;
static const CGFloat _buttonHeight = _buttonWidth;
static const CGFloat _titleWidth = 200;
static const CGFloat _titleXOffset = 26;
static NSString* const _reuseIdentifier = @"NotificationCell";

@interface STNotificationsCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

- (void)setupWithAlertItem:(id<STAlertItem>)item;

@property (nonatomic, readwrite, retain) UIView* title;
@property (nonatomic, readonly, retain) UIButton* apnsButton;
@property (nonatomic, readonly, retain) UIButton* emailButton;
@property (nonatomic, readonly, retain) UIImageView* apnsCheck;
@property (nonatomic, readonly, retain) UIImageView* emailCheck;
@property (nonatomic, readwrite, assign) STNotificationsViewController* controller;
@property (nonatomic, readwrite, copy) NSString* apnsType;
@property (nonatomic, readwrite, copy) NSString* emailType;

@end

@interface STNotificationsViewController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, retain) UIActivityIndicatorView* activityView;
@property (nonatomic, readwrite, retain) NSArray<STAlertItem>* items;
@property (nonatomic, readonly, retain) NSMutableSet* onSet;
@property (nonatomic, readonly, retain) NSMutableSet* offSet;
@property (nonatomic, readwrite, retain) STCancellation* cancellation;

- (void)setToggleId:(NSString*)toggleID toValue:(BOOL)value;

@end

@implementation STNotificationsViewController

@synthesize activityView = _activityView;
@synthesize items = _items;
@synthesize onSet = _onSet;
@synthesize offSet = _offSet;
@synthesize cancellation = _cancellation;

- (id)init
{
    self = [super initWithHeaderHeight:0];
    if (self) {
        _onSet = [[NSMutableSet alloc] init];
        _offSet = [[NSMutableSet alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [_activityView release];
    [_items release];
    [_onSet release];
    [_offSet release];
    [_cancellation cancel];
    [_cancellation release];
    [super dealloc];
}

+ (CGRect)apnsFrame {
    return CGRectMake(_apnsOffset, _buttonYOffset, _buttonWidth, _buttonHeight);
}

+ (CGRect)emailFrame {
    return CGRectMake(_emailOffset, _buttonYOffset, _buttonWidth, _buttonHeight);
}

- (void)setToggleId:(NSString *)toggleID toValue:(BOOL)value {
    if (value) {
        [self.onSet addObject:toggleID];
        [self.offSet removeObject:toggleID];
    }
    else {
        [self.offSet addObject:toggleID];
        [self.onSet removeObject:toggleID];
    }
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    _activityView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    _activityView.frame = CGRectMake(0, 0, self.view.frame.size.width, self.view.frame.size.height);
    [self.view addSubview:_activityView];
    _activityView.hidesWhenStopped = YES;
    
    CGFloat headerYPadding = 6;
    UIView* headerView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, 50)] autorelease];
    STChunk* startChunk = [STChunk chunkWithLineHeight:16 andWidth:200];
    STTextChunk* textChunk = [[[STTextChunk alloc] initWithPrev:startChunk 
                                                           text:@"Push & Email"
                                                           font:[UIFont stampedBoldFontWithSize:12]
                                                          color:[UIColor stampedDarkGrayColor]] autorelease];
    textChunk.bottomLeft = CGPointMake(_titleXOffset, 26);
    STChunksView* chunkView = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:textChunk]] autorelease];
    [Util reframeView:chunkView withDeltas:CGRectMake(0, headerYPadding, 0, 0)];
    [headerView addSubview:chunkView];

    UIImageView* apnsView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"notifications-push-icon"]] autorelease];
    apnsView.frame = [STNotificationsViewController apnsFrame];
    [Util reframeView:apnsView withDeltas:CGRectMake(0, headerYPadding, 0, 0)];
    [headerView addSubview:apnsView];
    
    UIImageView* emailView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"notifications-email-icon"]] autorelease];
    emailView.frame = [STNotificationsViewController emailFrame];
    [Util reframeView:emailView withDeltas:CGRectMake(0, headerYPadding, 0, 0)];
    [headerView addSubview:emailView];
    self.tableView.delegate = self;
    self.tableView.dataSource = self;
    self.tableView.tableHeaderView = headerView;
    self.tableView.backgroundColor = [UIColor clearColor];
    [self.activityView startAnimating];
    STNavigationItem *button = [[[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Save", @"Save") 
                                                                  style:UIBarButtonItemStyleDone 
                                                                 target:self 
                                                                 action:@selector(save:)] autorelease];
    
    STNavigationItem *cancelButton = [[[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") 
                                                                        style:UIBarButtonItemStyleDone
                                                                       target:self 
                                                                       action:@selector(cancel:)] autorelease];
    self.navigationItem.leftBarButtonItem = cancelButton;
    self.navigationItem.rightBarButtonItem = button;
    [self reloadStampedData];
}

- (void)reloadStampedData {
    if (!self.cancellation) {
        self.cancellation = [[STStampedAPI sharedInstance] alertsWithCallback:^(NSArray<STAlertItem> *alerts, NSError *error, STCancellation *cancellation) {
            [self handleResponse:alerts error:error andCancellation:cancellation];
        }];
    }
}

- (void)handleResponse:(NSArray<STAlertItem>*)alerts error:(NSError*)error andCancellation:(STCancellation*)cancelation {
    self.cancellation = nil;
    if (alerts) {
        [self.onSet removeAllObjects];
        [self.offSet removeAllObjects];
        self.items = alerts;
        [self.tableView reloadData];
        [self.activityView stopAnimating];
    }
    else {
        [Util warnWithAPIError:error andBlock:^{
            [Util compareAndPopController:self animated:YES];
        }];
    }
}


- (void)save:(id)sender {
    if (!self.cancellation) {
        [self.activityView startAnimating];
        self.cancellation = [[STStampedAPI sharedInstance] alertsWithOnIDs:[self.onSet allObjects]
                                                                    offIDs:[self.offSet allObjects]
                                                               andCallback:^(NSArray<STAlertItem> *alerts, NSError *error, STCancellation *cancellation) {
                                                                   [self handleResponse:alerts error:error andCancellation:cancellation]; 
                                                                   if (alerts) {
                                                                       [Util compareAndPopController:self animated:YES];
                                                                   }
                                                               }];
    }
}

- (void)cancel:(id)sender {
    [Util compareAndPopController:self animated:YES];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return self.items.count;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return 46;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STAlertItem> item = [self.items objectAtIndex:indexPath.row];
    STNotificationsCell* cell = [self.tableView dequeueReusableCellWithIdentifier:_reuseIdentifier];
    if (!cell) {
        cell = [[[STNotificationsCell alloc] initWithReuseIdentifier:_reuseIdentifier] autorelease];
        cell.controller = self;
    }
    [cell setupWithAlertItem:item];
    return cell;
}

@end

@implementation STNotificationsCell

@synthesize title = _title;
@synthesize apnsButton = _apnsButton;
@synthesize emailButton = _emailButton;
@synthesize apnsCheck = _apnsCheck;
@synthesize emailCheck = _emailCheck;
@synthesize apnsType = _apnsType;
@synthesize emailType = _emailType;
@synthesize controller = _controller;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
    if (self) {
        UIImage* buttonImage = [UIImage imageNamed:@"notifications-checkbox"];
        UIImage* checkImage = [UIImage imageNamed:@"notifications-checkmark"];
        _apnsButton = [[UIButton buttonWithType:UIButtonTypeCustom] retain];
        _apnsButton.frame = [STNotificationsViewController apnsFrame];
        [_apnsButton setImage:buttonImage forState:UIControlStateNormal];
        [_apnsButton addTarget:self action:@selector(toggleAPNS:) forControlEvents:UIControlEventTouchUpInside];
        [self.contentView addSubview:_apnsButton];
        _apnsCheck = [[UIImageView alloc] initWithImage:checkImage];
        _apnsCheck.frame = _apnsButton.frame;
        [self.contentView addSubview:_apnsCheck];
        _emailButton = [[UIButton buttonWithType:UIButtonTypeCustom] retain];
        [_emailButton setImage:buttonImage forState:UIControlStateNormal];
        [_emailButton addTarget:self action:@selector(toggleEmail:) forControlEvents:UIControlEventTouchUpInside];
        _emailButton.frame = [STNotificationsViewController emailFrame];
        [self.contentView addSubview:_emailButton];
        _emailCheck = [[UIImageView alloc] initWithImage:checkImage];
        _emailCheck.frame = _emailButton.frame;
        [self.contentView addSubview:_emailCheck];
        self.selectionStyle = UITableViewCellSelectionStyleNone;
    }
    return self;
}

- (void)dealloc
{
    [_title release];
    [_apnsButton release];
    [_emailButton release];
    [_apnsCheck release];
    [_emailCheck release];
    [_apnsType release];
    [_emailType release];
    [super dealloc];
}

- (void)toggleAPNS:(id)notImportant {
    if (self.apnsType) {
        self.apnsCheck.hidden = !self.apnsCheck.hidden;
        BOOL value = !self.apnsCheck.hidden;
        [self.controller setToggleId:self.apnsType toValue:value];
    }
}

- (void)toggleEmail:(id)notImportant {
    if (self.emailType) {
        self.emailCheck.hidden = !self.emailCheck.hidden;
        BOOL value = !self.emailCheck.hidden;
        [self.controller setToggleId:self.emailType toValue:value];
    }
}

- (void)setupWithAlertItem:(id<STAlertItem>)item {
    [self.title removeFromSuperview];
    self.title = nil;
    self.emailType = nil;
    self.apnsType = nil;
    self.apnsButton.hidden = YES;
    self.emailButton.hidden = YES;
    self.apnsCheck.hidden = YES;
    self.emailCheck.hidden = YES;
    STChunk* titleStart = [STChunk chunkWithLineHeight:16 andWidth:_titleWidth];
    STTextChunk* titleChunk = [[[STTextChunk alloc] initWithPrev:titleStart
                                                            text:[item name]
                                                            font:[UIFont stampedFontWithSize:12]
                                                           color:[UIColor stampedDarkGrayColor]] autorelease];
    titleChunk.bottomLeft = CGPointMake(_titleXOffset, 26);
    self.title = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:titleChunk]] autorelease];
    [self.contentView addSubview:self.title];
    for (id<STAlertToggle> toggle in item.toggles) {
        if (toggle.value && toggle.toggleID) {
            if ([[toggle type] isEqualToString:@"apns"]) {
                self.apnsButton.hidden = NO;
                self.apnsCheck.hidden = ![toggle.value boolValue];
                self.apnsType = [toggle toggleID];
            }
            else if ([[toggle type] isEqualToString:@"email"]) {
                self.emailButton.hidden = NO;
                self.emailCheck.hidden = ![toggle.value boolValue];
                self.emailType = [toggle toggleID];
            }
        }
    }
}

@end



//
//  PostStampViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "PostStampViewController.h"
#import "STStampDetailViewController.h"
#import "PostStampGraphView.h"
#import "PostStampHeaderView.h"
#import "STStampContainerView.h"
#import "STUsersViewController.h"
#import "PostStampBadgeTableCell.h"
#import "PostStampFriendsTableCell.h"
#import "STUserViewController.h"
#import "PostStampedByView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import "PostStampShareView.h"
#import "STBlockUIView.h"
#import "Util.h"
#import "STStampedAPI.h"
#import "QuartzUtils.h"
#import "STNavigationItem.h"
#import "STTwitter.h"
#import "STStampedByView.h"
#import "STTextChunk.h"
#import "STChunksView.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import <MessageUI/MFMailComposeViewController.h>

@interface PostStampFooterView : UIView

- (id)initWithStamp:(id<STStamp>)stamp stampedBy:(id<STStampedBy>)stampedBy andController:(PostStampViewController*)controller;

@property (nonatomic, readonly, retain) id<STStamp> stamp;
@property (nonatomic, readonly, retain) id<STStampedBy> stampedBy;

@end

@interface PostStampViewController () <MFMailComposeViewControllerDelegate>

@property(nonatomic,strong) PostStampHeaderView *headerView;
@property(nonatomic,strong) PostStampGraphView *graphView;
@property(nonatomic,strong) PostStampedByView *oldStampedByView;
@property(nonatomic,strong) id<STStamp> stamp;
@property(nonatomic,strong) id<STUserDetail> user;
@property(nonatomic,strong) id<STStampedBy> oldStampedBy;
@property(nonatomic,strong) NSArray *badges;
@property(nonatomic,assign) BOOL firstBadge;

@property (nonatomic, readwrite, assign) BOOL animatedAlready;

@property (nonatomic, readonly, retain) id<STStampedBy> stampedBy;
@property (nonatomic, readwrite, retain) STCancellation* stampedByCancellation;
@property (nonatomic, readonly, retain) PostStampFooterView* footerView;

@end

@implementation PostStampViewController

@synthesize graphView=_graphView;
@synthesize headerView=_headerView;
@synthesize stamp=_stamp;
@synthesize user=_user;
@synthesize oldStampedByView=_oldStampedByView;
@synthesize badges=_badges;
@synthesize firstBadge;
@synthesize oldStampedBy = _oldStampedBy;
@synthesize animatedAlready = _animatedAlready;

@synthesize stampedBy = _stampedBy;
@synthesize stampedByCancellation = _stampedByCancellation;
@synthesize footerView = _footerView;


- (id)initWithStamp:(id<STStamp>)stamp {
    if ((self = [super initWithStyle:UITableViewStylePlain])) {
        _stamp = [stamp retain];
        
        if (_stamp.badges.count) {
            
            NSMutableArray *array = [NSMutableArray array];
            
            for (id <STBadge> badge in _stamp.badges) {
                if ([badge.genre isEqualToString:@"entity_first_stamp"]) {
                    [array addObject:badge];
                    self.firstBadge = YES;
                }  else if ([badge.genre isEqualToString:@"user_first_stamp"]) {
                    [array addObject:badge];
                }
            }
            
            self.badges = array;
            
        } else {
            
            self.badges = [NSArray array];
            
        }
        
    }
    return self;
}

- (void)dealloc {
    [self.stampedByCancellation cancel];
    self.stampedByCancellation = nil;
    [_stampedBy release];
    [_footerView release];
    
    self.headerView = nil;
    self.graphView = nil;
    self.user = nil;
    self.stamp = nil;
    self.oldStampedBy = nil;
    self.oldStampedByView = nil;
    self.badges = nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    self.tableView.rowHeight = 160.0f;
    self.tableView.contentInset = UIEdgeInsetsMake(0.0f, 0.0f, 20.0f, 0.0f);
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.99f green:0.99f blue:0.99f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    self.tableView.backgroundView = background;
    [background release];
    
    if (!_headerView) {
        PostStampHeaderView *view = [[PostStampHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 58.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableHeaderView = view;
        _headerView = [view retain];
        _headerView.titleLabel.text = self.stamp.entity.title;
        [view release];
    }
    
    //    if (!_footerView && !self.stampedByCancellation) {
    //        self.stampedByCancellation = [[STStampedAPI sharedInstance] stampedByForEntityID:self.stamp.entity.entityID 
    //                                                                             andCallback:^(id<STStampedBy> stampedBy, NSError *error, STCancellation *cancellation) {
    //                                                                                 _stampedBy = [stampedBy retain];
    //                                                                                 if (stampedBy) {
    //                                                                                     [self createFooter];
    //                                                                                 }
    //                                                                                 else {
    //                                                                                     [Util warnWithAPIError:error andBlock:nil];
    //                                                                                 }
    //                                                                             }];
    //    }
    //    
    //    if (!_oldStampedByView) {
    //        PostStampedByView *view = [[PostStampedByView alloc] init];
    //        view.delegate = (id<PostStampedByViewDelegate>)self;
    //        self.oldStampedByView = view;
    //        [view release];        
    //    }
    
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)];
    self.navigationItem.rightBarButtonItem = button;
    [button release];
    [self reloadDataSource];
    
}

- (void)createFooter {
    _footerView = [[PostStampFooterView alloc] initWithStamp:self.stamp stampedBy:self.stampedBy andController:self];
    self.tableView.tableFooterView = _footerView;
}

- (void)viewDidUnload {
    self.oldStampedByView = nil;
    self.graphView = nil;
    [_footerView release];
    _footerView = nil;
    [self.stampedByCancellation cancel];
    self.stampedByCancellation = nil;
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [Util setTitle:[NSString stringWithFormat:@"Your Stamp"]
     forController:self];
    if (!self.animatedAlready) {
        self.headerView.stampView.alpha = 0;
        [Util executeWithDelay:.4 onMainThread:^{
            CGRect frameBefore = self.headerView.stampView.frame;
            self.headerView.stampView.frame = [Util scaledRectWithRect:frameBefore andScale:2];
            [UIView animateWithDuration:.2 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
                self.headerView.stampView.frame = frameBefore;
                self.headerView.stampView.alpha = 1;
            } completion:^(BOOL finished) {
                
            }];            
        }];
    }
    self.animatedAlready = YES;
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    [Util setTitle:nil
     forController:self];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}


#pragma mark - Actions

- (void)done:(id)sender {
    [[Util currentNavigationController] popToRootViewControllerAnimated:YES];
    
}


#pragma mark - UITableViewDataSource

- (void)resetContainer {
    
    if (!_tvContainer) {
        STStampContainerView *view = [[STStampContainerView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.tableView.bounds.size.width, [self.tableView rectForSection:0].size.height)];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self.tableView addSubview:view];
        [view release];
        _tvContainer = view;
    }
    
    [self.tableView sendSubviewToBack:_tvContainer];
    _tvContainer.frame = CGRectMake(0.0f, self.tableView.tableHeaderView.bounds.size.height + 4.0f, self.tableView.bounds.size.width, [self.tableView rectForSection:0].size.height + 6.0f);
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.row == 0) {
        return 150.0f;
    }
    
    if (indexPath.row <= self.badges.count) {
        return 76.0f;
    }
    
    return 105.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    NSInteger count = self.badges.count + 1;
    
    if (self.oldStampedBy) {
        count+=1;
    }
    
    return count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.row == 0) {
        
        [self resetContainer];
        
        static NSString *CellIdentifier = @"CellIdentifier";
        UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
        if (cell == nil) {
            
            cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:nil] autorelease];
            cell.layer.zPosition = 10;
            
            PostStampGraphView *graphView = [[PostStampGraphView alloc] initWithFrame:CGRectMake(0.0f, 10.0f, self.view.bounds.size.width, 140.0f)];
            if (self.stamp) {
                graphView.category = self.stamp.entity.category;
            }
            if (self.user) {
                graphView.user = self.user;
            } else {
                [graphView setLoading:YES];
            }
            [cell addSubview:graphView];
            self.graphView = graphView;
            [graphView release];  
            
        }
        return cell;
        
    }
    
    if (indexPath.row <= self.badges.count) {
        
        static NSString *BadgeCellIdentifier = @"BadgeCellIdentifier";
        PostStampBadgeTableCell *cell = [tableView dequeueReusableCellWithIdentifier:BadgeCellIdentifier];
        if (cell == nil) {
            cell = [[[PostStampBadgeTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:BadgeCellIdentifier] autorelease];
            cell.delegate = (id<PostStampBadgeTableCell>)self;
            cell.layer.zPosition = 10;
        }
        
        [cell showShadow:(indexPath.row==1)];
        [cell setupWithBadge:[self.badges objectAtIndex:indexPath.row-1]];
        
        return cell;
        
    }
    
    static NSString *FriendsCellIdentifier = @"FriendsCellIdentifier";
    PostStampFriendsTableCell *cell = [tableView dequeueReusableCellWithIdentifier:FriendsCellIdentifier];
    if (cell == nil) {
        cell = [[[PostStampFriendsTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:FriendsCellIdentifier] autorelease];
        cell.layer.zPosition = 10;
        cell.delegate = (id<PostStampFriendsTableCellDelegate>)self;
    }
    
    [cell showShadow:(indexPath.row==1)];
    [cell setupWithStampedBy:self.oldStampedBy andStamp:self.stamp];
    
    return cell;
    
}


#pragma mark - PostStampBadgeTableCell

- (void)postStampBadgeTableCellShare:(PostStampBadgeTableCell*)cell {
    //Check out my my first stamp with @stampedapp: [entity.title]. [link]
    [[STTwitter sharedInstance] fullTwitterAuthWithAddAccount:YES andCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
        if (success) {
            TWTweetComposeViewController* twitter = [[[TWTweetComposeViewController alloc] init] autorelease];
            NSString* text;
            if ([cell.badge.genre isEqualToString:@"user_first_stamp"]) {
                text = [NSString stringWithFormat:@"Check out my first stamp with @stampedapp: %@. %@", self.stamp.entity.title, self.stamp.URL];
            }
            else {
                text = [NSString stringWithFormat:@"I'm the first to stamp %@ on @stampedapp! %@", self.stamp.entity.title, self.stamp.URL];
            }
            [twitter setInitialText:text];
            
            if ([TWTweetComposeViewController canSendTweet]) {
                [self presentViewController:twitter animated:YES completion:nil];
            }
            
            twitter.completionHandler = ^(TWTweetComposeViewControllerResult result) {
                [self dismissModalViewControllerAnimated:YES];
            };
        }
        else {
            [Util warnWithAPIError:error andBlock:nil];
        }
    }];
    /*
     PostStampShareView *view = [[PostStampShareView alloc] initWithFrame:self.view.bounds];
     view.layer.zPosition = 100;
     [self.view addSubview:view];
     [view popIn];
     [view release];
     */
}


#pragma mark - PostStampFriendsTableCellDelegate

- (void)postStampFriendTableCell:(PostStampFriendsTableCell*)cell selectedStamp:(id<STStamp>)stamp {
    
    /*
     STUserViewController *controller = [[STUserViewController alloc] initWithUser:user];
     [self.navigationController pushViewController:controller animated:YES];
     [controller release];
     */
    
    STActionContext* context = [STActionContext contextInView:self.view];
    id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    
    
}


#pragma mark - PostStampedByViewDelegate

- (void)postStampedByView:(PostStampedByView*)view selectedPreview:(id<STStampPreview>)item {
    
    // STStampDetailViewController *controller = [[[STStampDetailViewController alloc] initWithStamp:item.stamp] autorelease];
    
    STActionContext* context = [STActionContext contextInView:self.view];
    id<STAction> action = [STStampedActions actionViewStamp:item.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    
}

- (void)postStampedByView:(PostStampedByView*)view selectedAll:(id)sender {
    
    NSMutableArray *userIDs = [NSMutableArray array];
    NSMutableDictionary* stamps = [NSMutableDictionary dictionary];
    for (id<STStampPreview> preview in [self.stampedBy.everyone stampPreviews]) {
        NSString *userID = preview.user.userID;
        NSString* stampID = preview.stampID;
        if (userID && stampID) {
            [userIDs addObject:userID];
            [stamps setObject:stampID forKey:userID];
        }
    }
    STUsersViewController *controller = [[[STUsersViewController alloc] initWithUserIDs:userIDs] autorelease];
    controller.userIDToStampID = stamps;
    [self.navigationController pushViewController:controller animated:YES];
    
}


#pragma mark - Datasource

- (void)reloadDataSource {
    
    id <STUser> user = [[STStampedAPI sharedInstance] currentUser];
    [[STStampedAPI sharedInstance] userDetailForUserID:user.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
        if (!error) {
            self.user = userDetail;
            [self.graphView setUser:self.user];
        } else {
            [self.graphView setLoading:YES];
        }
        [self resetContainer];
    }];
    
    if (!self.stamp || self.firstBadge) return; // ignore stamped by if the user is the first to stamp
    
    [[STStampedAPI sharedInstance] stampedByForEntityID:self.stamp.entity.entityID andCallback:^(id<STStampedBy> stampedBy, NSError *error, STCancellation *cancellation) {
        
        if (stampedBy) {
            
            self.oldStampedBy = stampedBy;
            _stampedBy = [stampedBy retain];
            [self.tableView beginUpdates];
            [self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:self.badges.count+1 inSection:0]] withRowAnimation:UITableViewRowAnimationFade];
            [self resetContainer];
            [self.tableView endUpdates];
            [self resetContainer];
            [Util executeWithDelay:.5 onMainThread:^{
                [self createFooter]; 
            }];
            
            self.oldStampedBy = stampedBy;
            
        }
    }];
    
}

- (void)shareToInstagram:(id)notImportant {
    [Util shareToInstagramFromController:self withImage:[UIImage imageNamed:@"instagram_sample.jpeg"]];
}

- (void)shareToTwitter:(id)notImportant {
    [Util shareToTwitterFromController:self withStamp:self.stamp];
}

- (void)shareToFacebook:(id)notImportant {
    
}

- (void)shareToEmail:(id)notImportant {
    MFMailComposeViewController* vc = [Util mailComposeViewControllerForStamp:self.stamp];
    vc.mailComposeDelegate = self;
    [self presentModalViewController:vc animated:YES];
}


- (void)mailComposeController:(MFMailComposeViewController*)controller 
          didFinishWithResult:(MFMailComposeResult)result
                        error:(NSError*)error {
    if (error) {
        [Util warnWithMessage:@"Couldn't send email" andBlock:^{
            [self dismissModalViewControllerAnimated:YES];
        }];
    }
    else {
        [self dismissModalViewControllerAnimated:YES];
    }
}


@end


@implementation PostStampFooterView

@synthesize stamp = _stamp;
@synthesize stampedBy = _stampedBy;

- (id)initWithStamp:(id<STStamp>)stamp stampedBy:(id<STStampedBy>)stampedBy andController:(PostStampViewController*)controller {
    self = [super initWithFrame:CGRectMake(0, 0, 320, 10)];
    if (self) {
        _stamp = [stamp retain];
        _stampedBy = [stampedBy retain];
        
        NSMutableArray* chunks = [NSMutableArray array];
        STChunk* shareStart = [STChunk chunkWithLineHeight:16 andWidth:290];
        STTextChunk* sharedHeader = [[[STTextChunk alloc] initWithPrev:shareStart
                                                                  text:@"Share your stamp"
                                                                  font:[UIFont stampedBoldFontWithSize:12]
                                                                 color:[UIColor stampedGrayColor]] autorelease];
        STChunk* sharedBodyStart = [STChunk newlineChunkWithPrev:shareStart];
        STTextChunk* sharedBody = [[[STTextChunk alloc] initWithPrev:sharedBodyStart
                                                                text:@"There's several unique ways to do so."
                                                                font:[UIFont stampedFontWithSize:12]
                                                               color:[UIColor stampedGrayColor]] autorelease];
        [chunks addObject:sharedHeader];
        [chunks addObject:sharedBody];
        STChunksView* chunksView = [[[STChunksView alloc] initWithChunks:chunks] autorelease];
        chunksView.frame = [Util centeredAndBounded:chunksView.frame.size inFrame:CGRectMake(0, 0, self.frame.size.width, chunksView.frame.size.height)];
        [Util appendView:chunksView toParentView:self];
        [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 5)];
        CGFloat xOffset = 15;
        CGFloat yOffset = self.frame.size.height;
        NSMutableArray* services = [NSMutableArray arrayWithObjects:
                                    @"instagram",
                                    @"twitter",
                                    @"facebook",
                                    @"email",
                                    nil];
        for (NSString* service in services) {
            SEL action = nil;
            if ([service isEqualToString:@"instagram"]) {
                action = @selector(shareToInstagram:);
            }
            else if ([service isEqualToString:@"twitter"]) {
                if ([TWTweetComposeViewController canSendTweet]) {
                    action = @selector(shareToTwitter:);
                }
            }
            else if ([service isEqualToString:@"facebook"]) {
                action = @selector(shareToFacebook:);
            }
            else if ([service isEqualToString:@"email"]) {
                action = @selector(shareToEmail:);
            }
            if (action) {
                UIButton* shareButton = [UIButton buttonWithType:UIButtonTypeCustom];
                UIImage* shareImage = [UIImage imageNamed:[NSString stringWithFormat:@"post_stamp_share_%@", service]];
                [shareButton setImage:shareImage forState:UIControlStateNormal];
                [shareButton addTarget:controller action:action forControlEvents:UIControlEventTouchUpInside];
                shareButton.frame = CGRectMake(xOffset, yOffset, shareImage.size.width, shareImage.size.height);
                [self addSubview:shareButton];
                xOffset = CGRectGetMaxX(shareButton.frame) + 7;
            }
        }
        
        [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 50)];
        
        STStampedByView* stampedByView = [[[STStampedByView alloc] initWithStampedBy:stampedBy
                                                                           blacklist:[NSSet setWithObject:stamp.user.userID]
                                                                            entityID:stamp.entity.entityID
                                                                      includeFriends:NO
                                                                         andDelegate:nil] autorelease];
        //        [self addSubview:stampedByView];
        [Util appendView:stampedByView toParentView:self];
    }
    return self;
}

- (void)dealloc
{
    [_stamp release];
    [_stampedBy release];
    [super dealloc];
}

@end












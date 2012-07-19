//
//  STMusicViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionViewController.h"
#import "STToolbarView.h"
#import "STGenericTableDelegate.h"
#import "STConsumptionLazyList.h"
#import "STFriendsSlice.h"
#import "STStampCellFactory.h"
#import "STCellStyles.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import "STButton.h"
#import "STStampedAPI.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STConfiguration.h"
#import "STConsumptionToolbarItem.h"
#import "STConsumptionToolbar.h"
#import "STGenericCellFactory.h"
#import "NoDataView.h"
#import "NoDataUtil.h"
#import "FindFriendsViewController.h"

static BOOL _hasShownPopUp = NO;

typedef enum {
    _animationStateNone = 0,
    _animationStateRunning,
    _animationStatePopUp,
    _animationStateFinished,
    _animationStateAbort,
} _animationState_t ;

//Film
static NSString* _movieNameKey = @"Consumption.film.movie.name";

static NSString* _inTheatersNameKey = @"Consumption.film.movie.inTheaters.name";
static NSString* _inTheatersFilterKey = @"Consumption.film.movie.inTheaters.filter";

static NSString* _onlineAndDVDNameKey = @"Consumption.film.movie.onlineAndDVD.name";
static NSString* _onlineAndDVDFilterKey = @"Consumption.film.movie.onlineAndDVD.filter";

static NSString* _tvNameKey = @"Consumption.film.tv.name";

//Music
static NSString* _artistNameKey = @"Consumption.music.artist.name";

static NSString* _albumNameKey = @"Consumption.music.album.name";

static NSString* _songNameKey = @"Consumption.music.song.name";

@interface STConsumptionViewController () <STConsumptionToolbarDelegate, STGenericTableDelegateDelegate>

- (STConsumptionToolbarItem*)setupToolbarItems;

@property (nonatomic, readonly, retain) STConsumptionLazyList* lazyList;
@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString* subcategory;
@property (nonatomic, readwrite, copy) NSString* filter;
@property (nonatomic, readonly, retain) STConsumptionToolbar* consumptionToolbar;
@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;
@property (nonatomic, readwrite, assign) _animationState_t animationState;
@property (nonatomic, readwrite, retain) UIView* popUp;
@property (nonatomic, readwrite, retain) UIView* tooltip;

@end

@implementation STConsumptionViewController

@synthesize tableDelegate = tableDelegate_;
@synthesize lazyList = lazyList_;
@synthesize category = category_;
@synthesize scope = scope_;
@synthesize subcategory = subcategory_;
@synthesize filter = filter_;
@synthesize consumptionToolbar = consumptionToolbar_;
@synthesize animationState = _animationState;
@synthesize tooltip = _tooltip;
@synthesize popUp = _popUp;

- (void)update {
    self.consumptionToolbar.scope = self.scope;
    self.tableDelegate.lazyList = [[[STConsumptionLazyList alloc] initWithScope:self.scope
                                                                        section:self.category
                                                                     subsection:self.subcategory] autorelease];
    [tableDelegate_ reloadStampedData];
}

- (STConsumptionToolbarItem*)setupToolbarItems {
    NSMutableArray* array = [NSMutableArray array];
    if ([self.category isEqualToString:@"film"]) {
        STConsumptionToolbarItem* movie = [[[STConsumptionToolbarItem alloc] init] autorelease];
        movie.name = [STConfiguration value:_movieNameKey];
        movie.value = @"movie";
        movie.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:movie];
        
        STConsumptionToolbarItem* tv = [[[STConsumptionToolbarItem alloc] init] autorelease];
        tv.name = [STConfiguration value:_tvNameKey];
        tv.value = @"tv";
        tv.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:tv];
    }
    else if ([self.category isEqualToString:@"book"]) {
        //None
    }
    else if ([self.category isEqualToString:@"music"]) {
        STConsumptionToolbarItem* artist = [[[STConsumptionToolbarItem alloc] init] autorelease];
        artist.value = @"artist";
        artist.name = [STConfiguration value:_artistNameKey];
        artist.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:artist];
        
        STConsumptionToolbarItem* albums = [[[STConsumptionToolbarItem alloc] init] autorelease];
        albums.value = @"album";
        albums.name = [STConfiguration value:_albumNameKey];
        albums.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:albums];
        
        STConsumptionToolbarItem* songs = [[[STConsumptionToolbarItem alloc] init] autorelease];
        songs.value = @"track";
        songs.iconValue = @"song";
        songs.name = [STConfiguration value:_songNameKey];
        songs.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:songs];
    }
    else if ([self.category isEqualToString:@"other"]) {
        
    }
    STConsumptionToolbarItem* rootItem = [[[STConsumptionToolbarItem alloc] init] autorelease];
    rootItem.type = STConsumptionToolbarItemTypeSection;
    rootItem.value = category_;
    rootItem.children = array;
    return rootItem;
}


- (void)noDataAction:(id)sender {
    
    FindFriendsViewController *controller = [[[FindFriendsViewController alloc] init] autorelease];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
    
}

- (void)showSmallTooltip {
    if (self.animationState != _animationStateAbort) {
        UIImageView* tooltip = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"taptoaddfriends"]] autorelease];
        [Util reframeView:tooltip withDeltas:CGRectMake(170 - 2.5, -40, 0, 0)];
        tooltip.alpha = 0;
        UILabel* label = [Util viewWithText:@""
                                       font:[UIFont stampedFontWithSize:10]
                                      color:[UIColor whiteColor]
                                       mode:UILineBreakModeTailTruncation
                                 andMaxSize:CGSizeMake(78, CGFLOAT_MAX)];
        label.frame = [Util centeredAndBounded:label.frame.size inFrame:CGRectMake(0, 0, 90, 38)];
        label.textAlignment = UITextAlignmentCenter;
        [tooltip addSubview:label];
        self.tooltip = tooltip;
        [self.consumptionToolbar addSubview:tooltip];
        [UIView animateWithDuration:.3
                         animations:^{
                             tooltip.alpha = 1;
                         } completion:^(BOOL finished) {
                             [Util executeWithDelay:4 onMainThread:^{
                                 if ([Util topController] == self) {
                                     [UIView animateWithDuration:.4 animations:^{
                                         tooltip.alpha = 0;
                                     } completion:^(BOOL finished) {
                                         [tooltip removeFromSuperview];
                                         self.tooltip = nil;
                                     }];
                                 } 
                             }];
                         }];
    }
}

- (void)exitNoDataView:(id)notImportant {
    [Util setFullScreenPopUp:nil dismissible:YES withBackground:[UIColor clearColor]];
    self.popUp = nil;
    self.animationState = _animationStateFinished;
    [self showSmallTooltip];
}

- (void)popUpDismissed:(NSNotification*)notification {
    if (notification.object == self.popUp) {
        self.animationState = _animationStateFinished;
        [self showSmallTooltip];
    }
}

- (void)showScopeShiftPopup {
    if ([Util topController] == self) {
        NoDataView* noDataView = [[[NoDataView alloc] initWithFrame:[Util fullscreenFrame]] autorelease];
        //        [Util reframeView:noDataView withDeltas:CGRectMake(0, -50, 0, 0)];
        noDataView.userInteractionEnabled = YES;
        NSString* topString = @"Since you're not yet following anyone, we're showing you suggestions from Tastemakers.";
        //        NSString* bottomString = @"Got it.";
        UILabel* top = [Util viewWithText:topString
                                     font:[UIFont stampedBoldFontWithSize:14]
                                    color:[UIColor whiteColor]
                                     mode:UILineBreakModeWordWrap
                               andMaxSize:CGSizeMake(240, CGFLOAT_MAX)];
        top.textAlignment = UITextAlignmentCenter;
        CGRect bounds = CGRectMake(0, 0, noDataView.imageView.frame.size.width, noDataView.imageView.frame.size.height);
        top.frame = [Util centeredAndBounded:top.frame.size inFrame:bounds];
        [noDataView.imageView addSubview:top];
        [Util reframeView:top withDeltas:CGRectMake(0, - 8 , 0, 0)];
        noDataView.imageView.userInteractionEnabled = YES;
        UIButton* exitButton = [UIButton buttonWithType:UIButtonTypeCustom];
        [exitButton addTarget:self action:@selector(exitNoDataView:) forControlEvents:UIControlEventTouchUpInside];
        [exitButton setImage:[UIImage imageNamed:@"closebutton_black"] forState:UIControlStateNormal];
        exitButton.frame = CGRectMake(-6.5, - 11, 48, 48);
        [noDataView.imageView addSubview:exitButton];
        
        //noDataView.frame = [Util centeredAndBounded:noDataView.frame.size inFrame:CGRectMake(0, 0, self.view.frame.size.width, self.view.frame.size.height)];
        noDataView.backgroundColor = [UIColor clearColor];
        //        [self.view addSubview:noDataView];
        //        self.emptyPopupView = noDataView;
        top.hidden = YES;
        //        bottom.hidden = YES;
        CGRect rectAfter = noDataView.imageView.frame;
        [Util setFullScreenPopUp:noDataView dismissible:YES withBackground:[UIColor clearColor]];
        noDataView.imageView.frame = [Util centeredAndBounded:CGSizeMake(20, 14) inFrame:rectAfter];
        [noDataView addGestureRecognizer:[[[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(exitNoDataView:)] autorelease]];
        [UIView animateWithDuration:.2 delay:0 options:UIViewAnimationCurveEaseInOut animations:^{
            noDataView.backgroundColor = [UIColor colorWithWhite:0 alpha:.3];
            noDataView.imageView.frame = rectAfter;
        } completion:^(BOOL finished) {
            top.hidden = NO;
            
        }];
        noDataView.userInteractionEnabled = YES;
    }
}

- (void)sliderWillShow:(id)notImportant {
    self.animationState = _animationStateAbort;
    [self.tooltip removeFromSuperview];
    self.tooltip = nil;
}

- (id)initWithCategory:(NSString*)category
{
    self = [super initWithHeaderHeight:0];
    if (self) {
        category_ = [category retain];
//        if (_hasShownPopUp) {
//            _animationState = _animationStateAbort;
//        }
        // Custom initialization
        if (LOGGED_IN) {
            scope_ = STStampedAPIScopeFriends;
        }
        else {
            scope_ = STStampedAPIScopeEveryone;
        }
//        
//        NSString* userDefaultsKey = @"38c14bb3f746a468f71cb0323bd9830a"; //psuedo-random
//        NSString* lastUserID = [[NSUserDefaults standardUserDefaults] objectForKey:userDefaultsKey];
//        NSString* currentUserID = [STStampedAPI sharedInstance].currentUser.userID;
//        if (currentUserID != nil && ![currentUserID isEqualToString:lastUserID]) {
//            _animationState = _animationStateNone;
//        }
//        else {
//            _animationState = _animationStateAbort;
//        }
//        [[NSUserDefaults standardUserDefaults] setObject:currentUserID ? currentUserID : @" invalid userID " forKey:userDefaultsKey];
//        
        tableDelegate_ = [[STGenericTableDelegate alloc] init];
        tableDelegate_.delegate = self;
        tableDelegate_.style = STCellStyleConsumption;
        tableDelegate_.lazyList = lazyList_;
        tableDelegate_.tableViewCellFactory = [STGenericCellFactory sharedInstance];
        __block STConsumptionViewController* weak = self;
        tableDelegate_.tableShouldReloadCallback = ^(id<STTableDelegate> tableDelegate) {
            [weak.tableView reloadData];
            if (self.animationState == _animationStateRunning) {
                self.animationState = _animationStatePopUp;
                [Util executeWithDelay:.3 onMainThread:^{
                    if ([Util topController] == self && self.animationState != _animationStateAbort) {
                        [self.consumptionToolbar.slider setScope:STStampedAPIScopeEveryone animated:YES];
                        if (_hasShownPopUp) {
//                            [Util executeWithDelay:.4 onMainThread:^{
//                                [self showSmallTooltip];
//                            }];
                        }
                        else {
                            [Util executeWithDelay:.4 onMainThread:^{
                                [self showScopeShiftPopup];
                            }];
                            _hasShownPopUp = YES;
                        }
                    }
                }];
            }
        };
        tableDelegate_.noDataFactory = ^(id<STTableDelegate> tableDelegate, UITableView* tableView) {
            CGRect bounds = CGRectMake(0, 0, tableView.frame.size.width, tableView.frame.size.height);
            UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"NONE"] autorelease];
            cell.selectionStyle = UITableViewCellSelectionStyleNone;
            if (self.animationState == _animationStateRunning || self.animationState == _animationStatePopUp) {
                NSString* title = @"No friends suggestions";
                NSString* body = nil;
                UIView* noData = [NoDataUtil waterMarkWithImage:[UIImage imageNamed:@"watermark_theguide"] title:title body:body options:nil];
                noData.frame = [Util centeredAndBounded:noData.frame.size inFrame:bounds];
                [cell.contentView addSubview:noData];
            }
            else if (weak.scope == STStampedAPIScopeFriends) {
                NoDataView* view = [[[NoDataView alloc] initWithFrame:bounds] autorelease];
                [view setupWithButtonTitle:@"Find friends to follow" detailTitle:@"Add friends to see their suggestions." target:weak andAction:@selector(noDataAction:)];
                view.frame = [Util centeredAndBounded:view.frame.size inFrame:CGRectMake(0, 0, tableView.frame.size.width, tableView.frame.size.height)];
                [cell.contentView addSubview:view];
            }
            else {
                NSString* title = nil;
                NSString* body = nil;
                if (weak.scope == STStampedAPIScopeYou) {
                    title = @"Sorry, no suggestions";
                    body = @"Add to-do's or create stamps!";
                }
                UIView* noData = [NoDataUtil waterMarkWithImage:[UIImage imageNamed:@"watermark_theguide"] title:title body:body options:nil];
                noData.frame = [Util centeredAndBounded:noData.frame.size inFrame:bounds];
                [cell.contentView addSubview:noData];
            }
            return cell;
        };
        [self update];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(popUpDismissed:) name:STUtilPopupDismissedNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(sliderWillShow:) name:STConsumptionToolbarSliderWillShowNotification object:nil];
    }
    return self;
}

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [tableDelegate_ release];
    [lazyList_ release];
    [category_ release];
    [subcategory_ release];
    [filter_ release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    self.tableView.delegate = self.tableDelegate;
    self.tableView.dataSource = self.tableDelegate;
}

- (void)viewDidUnload
{
    [super viewDidUnload];
}

- (void)viewDidDisappear:(BOOL)animated {
    [Util setFullScreenPopUp:nil dismissible:NO withBackground:[UIColor clearColor]];
    self.animationState = _animationStateAbort;
    [self.tooltip removeFromSuperview];
    [super viewDidDisappear:animated];
}

- (UIView *)loadToolbar {
    if (LOGGED_IN) {
        STConsumptionToolbarItem* rootItem = [self setupToolbarItems];
        consumptionToolbar_ = [[STConsumptionToolbar alloc] initWithRootItem:rootItem andScope:STStampedAPIScopeFriends];
        consumptionToolbar_.slider.delegate = (id<STSliderScopeViewDelegate>)self;
        consumptionToolbar_.delegate = self;
        return consumptionToolbar_;
    }
    else {
        return nil;
    }
}

- (void)unloadToolbar {
    [consumptionToolbar_ release];
    consumptionToolbar_ = nil;
}

- (void)setScope:(STStampedAPIScope)scope {
    scope_ = scope;
    [self update];
}

- (void)toolbar:(STConsumptionToolbar*)toolbar 
  didMoveToItem:(STConsumptionToolbarItem*)item 
           from:(STConsumptionToolbarItem*)previous {
    self.animationState = _animationStateAbort;
    if (item.type == STConsumptionToolbarItemTypeSection) {
        self.subcategory = nil;
        self.filter = nil;
    }
    else if (item.type == STConsumptionToolbarItemTypeSubsection) {
        self.filter = nil;
        self.subcategory = item.value;
    }
    else if (item.type == STConsumptionToolbarItemTypeFilter) {
        self.filter = item.value;
        self.subcategory = item.parent.value;
    }
    [self update];
}

- (void)cancelPendingRequests {
    [self.tableDelegate cancelPendingRequests];
}

- (void)reloadStampedData {
    [super reloadStampedData];
    [self.tableDelegate reloadStampedData];
}

+ (void)setupConfigurations {    
    //Film
    //Movie
    [STConfiguration addString:@"Movies" forKey:_movieNameKey];
    
    [STConfiguration addString:@"In Theaters" forKey:_inTheatersNameKey];
    [STConfiguration addString:@"in_theaters" forKey:_inTheatersFilterKey];
    
    [STConfiguration addString:@"Online/DVD" forKey:_onlineAndDVDNameKey];
    [STConfiguration addString:@"online_and_dvd" forKey:_onlineAndDVDFilterKey];
    
    //TV
    [STConfiguration addString:@"TV" forKey:_tvNameKey];
    
    //Music
    //Artist
    [STConfiguration addString:@"Artists" forKey:_artistNameKey];
    
    //Album
    [STConfiguration addString:@"Albums" forKey:_albumNameKey];
    
    //Song
    [STConfiguration addString:@"Songs" forKey:_songNameKey];
    
    [STConsumptionToolbar setupConfigurations];
}

#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    self.scope = scope;
    
}

- (void)tableDelegate:(STGenericTableDelegate *)tableDelegate didFinishLoadingWithCount:(NSInteger)count {
    if (count == 0 && self.scope == STStampedAPIScopeFriends && _animationState == _animationStateNone) {
        self.animationState = _animationStateRunning;
    }
}

@end

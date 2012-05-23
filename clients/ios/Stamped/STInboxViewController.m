//
//  STInboxViewController.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxViewController.h"
#import "STToolbarView.h"
#import "STScopeSlider.h"
#import "STUserStampsSliceList.h"
#import "STGenericTableDelegate.h"
#import "STYouStampsList.h"
#import "STStampCellFactory.h"
#import "Util.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STGenericCellFactory.h"
#import "STFriendsStampsList.h"
#import "STFriendsOfFriendsStampsList.h"
#import "STButton.h"
#import "ECSlidingViewController.h"
#import "STTableDelegator.h"
#import "STSingleViewSource.h"
#import "STSearchField.h"
#import "STEveryoneStampsList.h"
#import "STSliderScopeView.h"
#import "STStampedActions.h"

#import "EntityDetailViewController.h"
#import "STStampCell.h"
#import "AccountManager.h"


@interface STInboxViewController ()

@property (nonatomic, readonly, retain) STSliderScopeView *slider;
@property (nonatomic, readonly, retain) Stamps *stamps;
@property (nonatomic, readonly, retain) Stamps *searchStamps;

@end

@implementation STInboxViewController

@synthesize slider = _slider;
@synthesize stamps = _stamps;
@synthesize searchStamps = _searchStamps;

- (id)init {
  if (self = [super init]) {
      
      _stamps = [[Stamps alloc] init];
      _stamps.identifier = [[self class] description];
      
      [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(stampsChanged:) name:[NSString stringWithFormat:@"stamps-%@", _stamps.identifier] object:nil];

      if ([AccountManager sharedManager].currentUser == nil) {
          _stamps.scope = STStampedAPIScopeEveryone;
      } else {
          _stamps.scope = STStampedAPIScopeFriends;
      }
      
  }
  return self;
}

- (void)dealloc {
    
    if (_searchStamps) {
        [_searchStamps release], _searchStamps=nil;
    }
    [_stamps release], _stamps=nil;
    [_slider release], _slider=nil;
    
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
  
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];

    [Util addHomeButtonToController:self withBadge:YES];
    [Util addCreateStampButtonToController:self];
    
    if (!_slider) {
        _slider = [[STSliderScopeView alloc] initWithFrame:CGRectMake(0, 0.0f, self.view.bounds.size.width, 54)];
        _slider.delegate = (id<STSliderScopeViewDelegate>)self;
        self.footerView = _slider;
        _slider.scope = _stamps.scope;
    }
    self.showsSearchBar = YES;
    [self reloadDataSource];
    
    
    UIView *header = [[UIView alloc] initWithFrame:CGRectMake(0.0f, -300.0f, self.view.bounds.size.width, 241.0f)];
    header.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    header.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    [self.tableView addSubview:header];
    [header release];
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    [_slider release];
}

- (void)viewDidDisappear:(BOOL)animated {
    [super viewDidDisappear:animated];
}


#pragma mark - Stamps Notifications 

- (void)stampsChanged:(NSNotification *)notification {
    
    NSInteger sections = [self.tableView numberOfSections];
    UITableView *tableView = self.searching ? _searchResultsTableView : self.tableView;
    
    if (sections == 0 && ![_stamps isEmpty]) {
        
        [tableView beginUpdates];
        [tableView insertSections:[NSIndexSet indexSetWithIndex:0] withRowAnimation:UITableViewRowAnimationFade];
        [tableView endUpdates];
        
    } else {
        
        CGPoint offset = tableView.contentOffset;
        [tableView reloadData];
        tableView.contentOffset = offset;
        
    }

    [self dataSourceDidFinishLoading];

}


#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    [_stamps setScope:scope];
    [self.tableView reloadData];
    [self dataSourceDidFinishLoading];
    [self.tableView setContentOffset:CGPointMake(0.0f, 48.0f)];
    [self reloadDataSource];
}


#pragma mark - UITableViewDataSouce

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STStamp> stamp = [(tableView == _searchResultsTableView) ? _searchStamps : _stamps stampAtIndex:indexPath.row];
    return [STStampCell heightForStamp:stamp];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    
    if (tableView == _searchResultsTableView) {
        return [_searchStamps isEmpty] ? 0 : 1;
    }
    
    return [_stamps isEmpty] ? 0 : 1;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    if (tableView == _searchResultsTableView) {
        return [_searchStamps numberOfStamps];
    }
    
    return [_stamps numberOfStamps];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  
    static NSString *CellIdentifier = @"CellIdentifier";
    
    STStampCell *cell = (STStampCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    id<STStamp> stamp = [(tableView == _searchResultsTableView) ? _searchStamps : _stamps stampAtIndex:indexPath.row];
    [cell setupWithStamp:stamp];
    
    return cell;
  
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {

    id<STStamp> stamp = [(tableView == _searchResultsTableView) ? _searchStamps :_stamps stampAtIndex:indexPath.row];
    [[STStampedActions sharedInstance] viewStampWithStampID:stamp.stampID];
    
}


#pragma mark STSearchViewDelegate

- (void)stSearchViewDidCancel:(STSearchView*)view {
    [super stSearchViewDidCancel:view];
    
    // cancel model query
    
}

- (void)stSearchViewDidEndSearching:(STSearchView*)view {
    [super stSearchViewDidEndSearching:view];
    
    if (_searchStamps) {
        [_searchStamps release], _searchStamps=nil;
    }
    
}

- (void)stSearchViewDidBeginSearching:(STSearchView *)view {
    [super stSearchViewDidBeginSearching:view];
    
    if (!_searchStamps) {
        _searchStamps = [[Stamps alloc] init];
        _searchStamps.identifier = [[self class] description];
    }
    
}

- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text {
    [super stSearchView:view textDidChange:text];
    _stamps.searchQuery = text;
}

- (void)stSearchViewHitSearch:(STSearchView *)view withText:(NSString*)text {
    
    [_searchStamps searchWithQuery:text];
    
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return [_stamps isReloading];
}

- (void)loadNextPage {
    [_stamps loadNextPage];
}

- (BOOL)dataSourceHasMoreData {
    return [_stamps hasMoreData];
}

- (void)reloadDataSource {
    [_stamps reloadData];
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return [_stamps isEmpty];
}

- (void)setupNoDataView:(NoDataView*)view {

    view.imageView.userInteractionEnabled = YES;
    [[view.imageView subviews] makeObjectsPerformSelector:@selector(removeFromSuperview)];
    
    if (_stamps.scope == STStampedAPIScopeYou) {
        
        view.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
        view.imageView.backgroundColor = view.backgroundColor;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.lineBreakMode = UILineBreakModeWordWrap;
        label.numberOfLines = 3;
        label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        label.font = [UIFont boldSystemFontOfSize:13];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.textAlignment = UITextAlignmentCenter;
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
        [view.imageView addSubview:label];
        [label release];
        
        label.text = @"That amazing burrito place.\nThe last great book you read.\nA movie your friends have to see.";
        
        CGSize size = [label.text sizeWithFont:label.font constrainedToSize:CGSizeMake(240.0f, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
        CGRect frame = label.frame;
        frame.size = size;
        frame.origin.x = floorf((view.imageView.bounds.size.width-size.width)/2);
        frame.origin.y = 24.0f;
        label.frame = frame;
        
        CGFloat maxY = CGRectGetMaxY(label.frame);
        
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.lineBreakMode	= UILineBreakModeTailTruncation;
        label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        label.font = [UIFont boldSystemFontOfSize:17];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
        [view.imageView addSubview:label];
        [label release];
        
        label.text = @"Stamp it.";
        [label sizeToFit];
        
        frame = label.frame;
        frame.origin.x = floorf((view.imageView.bounds.size.width-frame.size.width)/2);
        frame.origin.y = floorf(maxY + 4.0f);
        label.frame = frame;
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(noDataTapped:)];
        [view addGestureRecognizer:gesture];
        [gesture release];
        
    } else {
        
        UIImage *image = [UIImage imageNamed:@"no_data_find_friends_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setTitle:@"Find friends to follow" forState:UIControlStateNormal];
        [button addTarget:self action:@selector(findFriends:) forControlEvents:UIControlEventTouchUpInside];
        [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.9f] forState:UIControlStateNormal];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button sizeToFit];
        [view.imageView addSubview:button];
        CGRect frame = button.frame;
        frame.origin.y = 34.0f;
        frame.size.width += 48.0f;
        frame.size.height = image.size.height;
        frame.origin.x = (view.imageView.bounds.size.width - frame.size.width)/2;
        button.frame = frame;
        CGFloat maxY = CGRectGetMaxY(button.frame);

        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.font = [UIFont systemFontOfSize:12];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
        [view.imageView addSubview:label];
        [label release];
        
        label.text = @"to view their stamps.";
        [label sizeToFit];
        
        frame = label.frame;
        frame.origin.x = floorf((view.imageView.bounds.size.width-frame.size.width)/2);
        frame.origin.y = floorf(maxY + 8.0f);
        label.frame = frame;
        
    }
    
 

}


#pragma mark - No Data Actions

- (void)findFriends:(id)sender {
    
    
}

- (void)noDataTapped:(UITapGestureRecognizer*)gesture {
    
    UIImageView *magnifyView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"no_data_magnify.png"]];
    
    UIGraphicsBeginImageContextWithOptions(magnifyView.bounds.size, YES, 0);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextScaleCTM(ctx, 1.2, 1.2);
    CGContextTranslateCTM(ctx, -((self.view.bounds.size.width-magnifyView.bounds.size.width)+20.0f), 0.0f);
    [self.navigationController.view.layer renderInContext:ctx];
    UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    UIView *view = [[UIView alloc] initWithFrame:self.navigationController.view.bounds];
    view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.3f];
    [self.navigationController.view addSubview:view];
    [view release];
    
    CGRect frame = magnifyView.frame;
    frame.origin.x = (view.bounds.size.width - (frame.size.width-24.0f));
    frame.origin.y = -30.0f;
    magnifyView.frame = frame;
    [view addSubview:magnifyView];
    [magnifyView release];

    UIImageView *imageView = [[UIImageView alloc] initWithImage:image];
    [view insertSubview:imageView atIndex:0];
    [imageView release];
    
    frame = imageView.frame;
    frame.origin.x = (view.bounds.size.width - imageView.frame.size.width);
    imageView.frame = frame;
    
    CALayer *layer = [CALayer layer];
    layer.frame = CGRectMake(32, -26.0f, imageView.bounds.size.width-18, imageView.bounds.size.height-18);
    layer.cornerRadius = ((imageView.bounds.size.width-18)/2);
    layer.backgroundColor = [UIColor blackColor].CGColor;
    imageView.layer.mask = layer;
    
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"backgroundColor"];
    animation.fromValue = (id)[UIColor clearColor].CGColor;
    animation.duration = 0.3f;
    [view.layer addAnimation:animation forKey:nil];
    
    double delayInSeconds = 4.0;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        [view removeFromSuperview];
    });
    
}


@end

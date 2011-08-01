//
//  InboxViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "InboxViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Entity.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "Stamp.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"

static const CGFloat kFilterRowHeight = 44.0;

typedef enum {
  StampsListFilterTypeBook,
  StampsListFilterTypeFilm,
  StampsListFilterTypeMusic,
  StampsListFilterTypePlace,
  StampsListFilterTypeOther,
  StampsListFilterTypeAll
} StampsListFilterType;

@interface InboxViewController ()
- (void)loadStampsFromDataStore;
- (void)loadStampsFromNetwork;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)rotateSpinner;
- (void)setIsLoading:(BOOL)loading;

@property (nonatomic, copy) NSArray* filterButtons;
@property (nonatomic, copy) NSArray* filteredStampsArray;
@property (nonatomic, copy) NSArray* stampsArray;
@property (nonatomic, assign) UIView* filterView;
@property (nonatomic, retain) UIButton* placesFilterButton;
@property (nonatomic, retain) UIButton* booksFilterButton;
@property (nonatomic, retain) UIButton* filmsFilterButton;
@property (nonatomic, retain) UIButton* musicFilterButton;
@end

@implementation InboxViewController

@synthesize filterButtons = filterButtons_;
@synthesize filterView = filterView_;
@synthesize filteredStampsArray = filteredStampsArray_;
@synthesize stampsArray = stampsArray_;
@synthesize placesFilterButton = placesFilterButton_;
@synthesize booksFilterButton = booksFilterButton_;
@synthesize filmsFilterButton = filmsFilterButton_;
@synthesize musicFilterButton = musicFilterButton_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.filterButtons = nil;
  self.filterView = nil;
  self.filteredStampsArray = nil;
  self.stampsArray = nil;
  self.placesFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmsFilterButton = nil;
  self.musicFilterButton = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];

  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(stampWasCreated:)
                                               name:kStampWasCreatedNotification
                                             object:nil];
  self.filterButtons =
      [NSArray arrayWithObjects:(id)placesFilterButton_,
                                (id)booksFilterButton_,
                                (id)filmsFilterButton_,
                                (id)musicFilterButton_, nil];
  
  self.tableView.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  [self loadStampsFromDataStore];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];

  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.filterView = nil;
  self.filterButtons = nil;
  self.filteredStampsArray = nil;
  self.stampsArray = nil;
  self.placesFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmsFilterButton = nil;
  self.musicFilterButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  if (!userDidScroll_)
    self.tableView.contentOffset = CGPointMake(0, kFilterRowHeight);
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)loadStampsFromDataStore {
  self.stampsArray = nil;
	NSFetchRequest* request = [Stamp fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
	self.stampsArray = [Stamp objectsWithFetchRequest:request];
  [self filterButtonPushed:nil];
}

- (void)loadStampsFromNetwork {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  NSString* userID = [AccountManager sharedManager].currentUser.userID;
  NSString* resourcePath = [NSString stringWithFormat:@"/collections/inbox.json?authenticated_user_id=%@", userID];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:stampMapping
                                  delegate:self];
}

- (void)stampWasCreated:(NSNotification*)notification {
  [self loadStampsFromDataStore];
  self.tableView.contentOffset = CGPointMake(0, kFilterRowHeight);
}

#pragma mark - Filter stuff

- (IBAction)filterButtonPushed:(id)sender {
  filteredStampsArray_ = nil;

  UIButton* selectedButton = (UIButton*)sender;
  for (UIButton* button in self.filterButtons)
    button.selected = (button == selectedButton && !button.selected);

  if (selectedButton && !selectedButton.selected) {
    self.filteredStampsArray = stampsArray_;
    [self.tableView reloadSections:[NSIndexSet indexSetWithIndex:0]
                  withRowAnimation:UITableViewRowAnimationMiddle];
    return;
  } else if (!selectedButton) {
    // Initial load from datastore.
    self.filteredStampsArray = stampsArray_;
    [self.tableView reloadData];
  }

  NSString* filterString = nil;
  if (selectedButton == placesFilterButton_) {
    filterString = @"Place";
  } else if (selectedButton == booksFilterButton_) {
    filterString = @"Book";
  } else if (selectedButton == filmsFilterButton_) {
    filterString = @"Film";
  } else if (selectedButton == musicFilterButton_) {
    filterString = @"Music";
  }
  if (filterString) {
    NSPredicate* filterPredicate = [NSPredicate predicateWithFormat:@"entityObject.category == %@", filterString];
    self.filteredStampsArray = [stampsArray_ filteredArrayUsingPredicate:filterPredicate];
    [self.tableView reloadSections:[NSIndexSet indexSetWithIndex:0]
                  withRowAnimation:UITableViewRowAnimationMiddle];
  }
}

- (void)setIsLoading:(BOOL)loading {
  if (isLoading_ == loading)
    return;

  isLoading_ = loading;
  shouldReload_ = NO;

  if (!loading) {
    [reloadLabel_.layer removeAllAnimations];
    reloadLabel_.text = @"Pull my finger. \ue231";
    reloadLabel_.layer.transform = CATransform3DIdentity;
    [UIView animateWithDuration:0.2
                          delay:0 
                        options:UIViewAnimationOptionBeginFromCurrentState
                     animations:^{
                       self.tableView.contentInset = UIEdgeInsetsZero;
                     }
                     completion:nil];
    return;
  }
  
  [UIView animateWithDuration:0.2
                        delay:0 
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     self.tableView.contentInset = UIEdgeInsetsMake(70, 0, 0, 0);
                   }
                   completion:nil];

  [self rotateSpinner];
}

- (void)rotateSpinner {
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanFalse forKey:kCATransactionDisableActions];
  [CATransaction setValue:[NSNumber numberWithFloat:2.0] forKey:kCATransactionAnimationDuration];
  
  CABasicAnimation* animation;
  animation = [CABasicAnimation animationWithKeyPath:@"transform.rotation.z"];
  animation.fromValue = [NSNumber numberWithFloat:0.0];
  animation.toValue = [NSNumber numberWithFloat:M_PI * 2];
  animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionLinear];
  animation.delegate = self;
  [reloadLabel_.layer addAnimation:animation forKey:@"rotationAnimation"];
  [CATransaction commit];
}

#pragma mark - CAAnimationDelegate methods.

- (void)animationDidStop:(CAAnimation*)anim finished:(BOOL)flag {
  if (isLoading_)
    [self rotateSpinner];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return [filteredStampsArray_ count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (cell == nil) {
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  cell.stamp = (Stamp*)[filteredStampsArray_ objectAtIndex:indexPath.row];
  
  return cell;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"LastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
	[self loadStampsFromDataStore];
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Error"
                                                   message:[error localizedDescription]
                                                  delegate:nil
                                         cancelButtonTitle:@"OK" otherButtonTitles:nil] autorelease];
	[alert show];
	NSLog(@"Hit error: %@", error);
  [self setIsLoading:NO];
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor whiteColor];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  StampDetailViewController* detailViewController =
      [[StampDetailViewController alloc] initWithStamp:[filteredStampsArray_ objectAtIndex:indexPath.row]];

  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  userDidScroll_ = YES;
  if (isLoading_)
    return;

  shouldReload_ = scrollView.contentOffset.y < -65.0;
  reloadLabel_.text = shouldReload_ ? @"\ue05a" : @"Pull my finger. \ue231";
}

- (void)scrollViewDidEndDragging:(UIScrollView*)scrollView willDecelerate:(BOOL)decelerate {
  if (shouldReload_) {
    [self setIsLoading:YES];
    [self loadStampsFromNetwork];
  }
}

@end

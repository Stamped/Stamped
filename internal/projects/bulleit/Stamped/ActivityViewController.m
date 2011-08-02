//
//  ActivityViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "ActivityCommentTableViewCell.h"
#import "ActivityCreditTableViewCell.h"
#import "Comment.h"
#import "Event.h"

@interface ActivityViewController ()
- (void)loadEventsFromDataStore;
- (void)loadEventsFromNetwork;

@property (nonatomic, copy) NSArray* eventsArray;
@end

@implementation ActivityViewController

@synthesize eventsArray = eventsArray_;

- (void)didReceiveMemoryWarning {
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)dealloc {
  self.eventsArray = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.tableView.allowsSelection = NO;
  [self loadEventsFromDataStore];
  [self loadEventsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.eventsArray = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)loadEventsFromDataStore {
  self.eventsArray = nil;
	NSFetchRequest* request = [Event fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
	self.eventsArray = [Event objectsWithFetchRequest:request];
  [self.tableView reloadData];
}

- (void)loadEventsFromNetwork {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* eventMapping = [objectManager.mappingProvider mappingForKeyPath:@"Event"];
  NSString* userID = [AccountManager sharedManager].currentUser.userID;
  NSString* resourcePath = [NSString stringWithFormat:@"/activity/show.json?authenticated_user_id=%@", userID];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:eventMapping
                                  delegate:self];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return [eventsArray_ count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [eventsArray_ objectAtIndex:indexPath.row];
  NSString* reuseIdentifier = @"CommentIdentifier";
  if ([event.genre isEqualToString:@"restamp"])
    reuseIdentifier = @"RestampIdentifier";

  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:reuseIdentifier];
  if (cell == nil) {
    if ([reuseIdentifier isEqualToString:@"RestampIdentifier"]) {
      cell = [[[ActivityCreditTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else {
      cell = [[[ActivityCommentTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    }
  }
  if ([cell respondsToSelector:@selector(setEvent:)])
    [(id)cell setEvent:event];

  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  if ([cell isMemberOfClass:[ActivityCommentTableViewCell class]]) {
    cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  } else {
    cell.backgroundColor = [UIColor whiteColor];
  }
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [eventsArray_ objectAtIndex:indexPath.row];
  if ([event.genre isEqualToString:@"comment"] ||
      [event.genre isEqualToString:@"reply"] ||
      [event.genre isEqualToString:@"mention"]) {
    CGSize stringSize = [event.comment.blurb sizeWithFont:[UIFont fontWithName:@"Helvetica" size:12]
                                        constrainedToSize:CGSizeMake(230, MAXFLOAT)
                                            lineBreakMode:UILineBreakModeWordWrap];
    return fmaxf(60.0, stringSize.height + 40);
  }

  return 63.0;
}


#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"LastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
  for (Event* e in objects) {
    if (!e.stamp)
      NSLog(@"Event's stamp is null: %@", e);
  }
	[self loadEventsFromDataStore];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Error"
                                                   message:[error localizedDescription]
                                                  delegate:nil
                                         cancelButtonTitle:@"OK" otherButtonTitles:nil] autorelease];
	[alert show];
	NSLog(@"Hit error: %@", error);
  //[self setIsLoading:NO];
}

@end

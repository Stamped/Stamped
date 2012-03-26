//
//  STStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailViewController.h"

#import "Entity.h"
#import "STStampDetailToolbar.h"
#import "Stamp.h"

static NSString* const kCreateFavoritePath = @"/favorites/create.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";
static NSString* const kCreateLikePath = @"/stamps/likes/create.json";
static NSString* const kRemoveLikePath = @"/stamps/likes/remove.json";

@interface STStampDetailViewController ()
@property (nonatomic, retain) Stamp* stamp;

- (void)_todoButtonPressed:(id)sender;
- (void)_likeButtonPressed:(id)sender;
@end

@implementation STStampDetailViewController

@synthesize stamp = _stamp;
@synthesize toolbar = _toolbar;

- (id)initWithStamp:(Stamp*)stamp {
  self = [super initWithNibName:@"STStampDetailViewController" bundle:nil];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)dealloc {
  [_stamp release];
  self.toolbar = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  _toolbar.likeButton.selected = _stamp.isLiked.boolValue;
  [_toolbar.likeButton addTarget:self
                          action:@selector(_likeButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
  _toolbar.todoButton.selected = _stamp.entityObject.favorite != nil;
  [_toolbar.todoButton addTarget:self
                          action:@selector(_todoButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.toolbar = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Private methods.

- (void)_todoButtonPressed:(id)sender {
  BOOL shouldRemove = _stamp.entityObject.favorite != nil;
  NSString* path = shouldRemove ? kRemoveFavoritePath : kCreateFavoritePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = favoriteMapping;
  if (shouldRemove) {
    objectLoader.params = [NSDictionary dictionaryWithObject:_stamp.entityObject.entityID forKey:@"entity_id"];
    _stamp.entityObject.favorite = nil;
    [Stamp.managedObjectContext save:NULL];
  } else {
    objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
                           _stamp.entityObject.entityID, @"entity_id",
                           _stamp.stampID, @"stamp_id", nil];
  }
  [objectLoader send];
}

- (void)_likeButtonPressed:(id)sender {
  BOOL shouldRemove = _stamp.isLiked.boolValue;
  NSString* path = shouldRemove ? kRemoveLikePath : kCreateLikePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:_stamp.stampID, @"stamp_id", nil];

  [objectLoader send];
}

@end

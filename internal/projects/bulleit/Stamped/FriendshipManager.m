//
//  FriendshipManager.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/8/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "FriendshipManager.h"

#import "AccountManager.h"
#import "Stamp.h"
#import "User.h"

static FriendshipManager* sharedFriendshipManager_ = nil;
static NSString* const kUserStampsPath = @"/collections/user.json";

@interface FriendshipManager ()
- (void)loadStampsForUserID:(NSString*)userID;

@property (nonatomic, retain) NSMutableDictionary* userToRequestDictionary;
@property (nonatomic, retain) NSMutableDictionary* userToOldestStampDateDictionary;
@end

@implementation FriendshipManager

@synthesize userToRequestDictionary = userToRequestDictionary_;
@synthesize userToOldestStampDateDictionary = userToOldestStampDateDictionary_;

+ (FriendshipManager*)sharedManager {
  if (!sharedFriendshipManager_)
    sharedFriendshipManager_ = [[super allocWithZone:NULL] init];

  return sharedFriendshipManager_;
}

+ (id)allocWithZone:(NSZone*)zone {
  return [[self sharedManager] retain];
}

- (id)copyWithZone:(NSZone*)zone {
  return self;
}

- (id)retain {
  return self;
}

- (NSUInteger)retainCount {
  return NSUIntegerMax;
}

- (oneway void)release {
  // Do nothin'.
}

- (id)autorelease {
  return self;
}

#pragma mark - Begin custom implementation.

- (id)init {
  self = [super init];
  if (self) {
    self.userToRequestDictionary = [NSMutableDictionary dictionary];
    self.userToOldestStampDateDictionary = [NSMutableDictionary dictionary];
  }
  return self;
}

- (void)followUser:(User*)user {
  User* currentUser = [AccountManager sharedManager].currentUser;
  [currentUser addFollowingObject:user];
  [User.managedObjectContext save:NULL];

  if ([userToRequestDictionary_.allKeys containsObject:user.userID])
    return;

  [self loadStampsForUserID:user.userID];
}

- (void)unfollowUser:(User*)user {
  User* currentUser = [AccountManager sharedManager].currentUser;
  [currentUser removeFollowingObject:user];
  RKObjectLoader* loader = [userToRequestDictionary_ objectForKey:user.userID];
  [loader cancel];
  [userToRequestDictionary_ removeObjectForKey:user.userID];
  [userToOldestStampDateDictionary_ removeObjectForKey:user.userID];
  NSFetchRequest* request = [Stamp fetchRequest];
  request.predicate = [NSPredicate predicateWithFormat:@"user.userID == %@", user.userID];
  NSArray* results = [Stamp objectsWithFetchRequest:request];
  for (Stamp* s in results)
    s.temporary = [NSNumber numberWithBool:YES];

  [Stamp.managedObjectContext save:NULL];
}

- (void)loadStampsForUserID:(NSString*)userID {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserStampsPath
                                                                    delegate:self];
  objectLoader.objectMapping = stampMapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:userID, @"user_id",
                                 @"1", @"quality", @"0", @"since", nil];
  NSDate* oldestInBatch = [userToOldestStampDateDictionary_ objectForKey:userID];
  if (oldestInBatch)
    [params setObject:[NSString stringWithFormat:@"%.0f", oldestInBatch.timeIntervalSince1970] forKey:@"before"];
  
  objectLoader.params = params;
  [userToRequestDictionary_ setObject:objectLoader forKey:userID];
  [objectLoader send];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSString* userID = nil;
  for (NSString* key in userToRequestDictionary_.allKeys) {
    if ([userToRequestDictionary_ objectForKey:key] == objectLoader) {
      userID = key;
      break;
    }
  }
  if (!userID)
    return;

  [userToRequestDictionary_ removeObjectForKey:userID];
  NSDate* oldestInBatch = [objects.lastObject modified];
  
  for (Stamp* s in objects)
    s.temporary = [NSNumber numberWithBool:NO];
  
  [Stamp.managedObjectContext save:NULL];
  if (objects.count < 10 || !oldestInBatch) {
    [userToOldestStampDateDictionary_ removeObjectForKey:userID];
  } else {
    [userToOldestStampDateDictionary_ setObject:oldestInBatch forKey:userID];
    [self loadStampsForUserID:userID];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [objectLoader send];
    return;
  }
}

@end

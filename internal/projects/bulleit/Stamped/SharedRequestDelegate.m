//
//  SharedRequestDelegate.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/20/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "SharedRequestDelegate.h"

#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Comment.h"
#import "StampDetailViewController.h"

static SharedRequestDelegate* sharedDelegate_ = nil;

@implementation SharedRequestDelegate

+ (SharedRequestDelegate*)sharedDelegate {
  if (sharedDelegate_ == nil)
    sharedDelegate_ = [[super allocWithZone:NULL] init];
  
  return sharedDelegate_;
}

+ (id)allocWithZone:(NSZone*)zone {
  return [[self sharedDelegate] retain];
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

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	if ([objectLoader.resourcePath isEqualToString:kRemoveCommentPath]) {
    Comment* comment = [objects lastObject];
    [Comment.managedObjectContext deleteObject:comment];
    [Comment.managedObjectContext save:NULL];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];
}

@end

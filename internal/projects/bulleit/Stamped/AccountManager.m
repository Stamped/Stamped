//
//  AccountManager.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "AccountManager.h"

static AccountManager* sharedAccountManager_ = nil;

@implementation AccountManager

+ (AccountManager*)sharedManager {
  if (sharedAccountManager_ == nil)
    sharedAccountManager_ = [[super allocWithZone:NULL] init];
  
  return sharedAccountManager_;
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

@end

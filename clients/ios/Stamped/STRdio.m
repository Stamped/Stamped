//
//  STRdio.m
//  Stamped
//
//  Created by Landon Judkins on 3/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRdio.h"
#import <Rdio/Rdio.h>

@interface STRdio ()

@property (nonatomic, readonly, retain) Rdio* rdio;
@property (nonatomic, readwrite, assing) BOOL loggedIn;
@property (nonatomic, readwrite, copy) NSString* accessToken;

@end

@implementation STRdio

@synthesize rdio = _rdio;
@synthesize loggedIn = _loggedIn;
@synthesize accessToken = _accessToken;

static STRdio* _sharedInstance;

- (id)init {
  self = [super init];
  if (self) {
    _rdio = [[Rdio alloc] initWithConsumerKey:@"bzj2pmrs283kepwbgu58aw47"
                                    andSecret:@"xJSZwBZxFp" delegate:viewController];
  }
  return self;
}

- (void)dealloc
{
  [_accessToken release];
  [_rdio release];
  [super dealloc];
}

+ (void)initialize {
  _sharedInstance = [[STRdio alloc] init];
}

+ (STRdio*)sharedRdio {
  return _sharedInstance;
}

- (void) rdioDidAuthorizeUser:(NSDictionary *)user withAccessToken:(NSString *)accessToken {
  self.loggedIn = YES;
  self.accessToken = accessToken;
}

- (void) rdioAuthorizationFailed:(NSString *)error {
  self.loggedIn = NO;
  self.accessToken = nil;
}

- (void) rdioAuthorizationCancelled {
  self.loggedIn = NO;
  self.accessToken = nil;
}

- (void) rdioDidLogout {
  self.loggedIn = NO;
  self.accessToken = nil;
}

@end

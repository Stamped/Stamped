//
//  STUserCollectionSlice.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserCollectionSlice.h"

@implementation STUserCollectionSlice

@synthesize userID = _userID;
@synthesize screenName = _screenName;

- (void)dealloc
{
  [_userID release];
  [_screenName release];
  [super dealloc];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [super asDictionaryParams];
    [dict setObject:@"user" forKey:@"scope"];
  if (self.userID) {
    [dict setObject:self.userID forKey:@"user_id"];
  }
  if (self.screenName) {
    [dict setObject:self.screenName forKey:@"screen_name"];
  }
  return dict;
}

- (void)importDictionaryParams:(NSDictionary*)params {
  [super importDictionaryParams:params];
  if ([params objectForKey:@"user_id"]) {
    self.userID = [params objectForKey:@"user_id"];
  }
  if ([params objectForKey:@"screen_name"]) {
    self.screenName = [params objectForKey:@"screen_name"];
  }
}


- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset {
  STUserCollectionSlice* copy = [super resizedSliceWithLimit:limit andOffset:offset];
  copy.userID = self.userID;
  copy.screenName = self.screenName;
  return copy;
}

@end

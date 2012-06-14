//
//  STImageUpload.m
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STImageUpload.h"

@implementation STImageUpload

@synthesize tempImageURL = tempImageURL_;

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* params = [super asDictionaryParams];
  id val = self.tempImageURL;
  if (val) {
    [params setObject:val forKey:@"temp_image_url"];
  }
  return params;
}

- (void)importDictionaryParams:(NSDictionary*)params {
  id val = [params objectForKey:@"temp_image_url"];
  if (val) {
    self.tempImageURL = val;
  }
  [super importDictionaryParams:params];
}

@end

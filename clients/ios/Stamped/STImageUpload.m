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
@synthesize tempImageHeight = tempImageHeight_;
@synthesize tempImageWidth = tempImageWidth_;

- (NSMutableDictionary*)asDictionaryParams {
  return [NSMutableDictionary dictionary];
}

- (void)importDictionaryParams:(NSDictionary*)params {
}

@end

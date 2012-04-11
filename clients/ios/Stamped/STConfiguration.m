//
//  STConfiguration.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConfiguration.h"

@implementation STConfiguration

static STConfiguration* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STConfiguration alloc] init];
}

+ (STConfiguration *)sharedInstance {
  return _sharedInstance;
}

- (NSInteger)internalVersion {
  return 1;
}

@end

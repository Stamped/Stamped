//
//  STStampFactory.m
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampFactory.h"

@interface STStampFactory ()

@property (nonatomic, readonly, retain) NSCache* cache;

@end

@implementation STStampFactory

@synthesize cache = _cache;

static STStampFactory* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STStampFactory alloc] init];
}

-(id)init {
  self = [super init];
  if (self) {
    _cache = [[NSCache alloc] init];
  }
  return self;
}

- (NSOperation*)stampWithStampId:(NSString*)anEntityID andCallbackBlock:(void (^)(id<STStamp>))aBlock {
  return nil;
}

+ (STStampFactory*)sharedInstance {
  return _sharedInstance;
}

@end

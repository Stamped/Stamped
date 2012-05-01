//
//  STAStampButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAStampButton.h"
#import "STStampedAPI.h"

@implementation STAStampButton

@synthesize stamp = _stamp;

- (id)initWithStamp:(id<STStamp>)stamp normalOffImage:(UIImage*)normalOffImage offText:(NSString*)offText andOnText:(NSString*)onText
{
  self = [super initWithNormalOffImage:normalOffImage offText:offText andOnText:onText];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)dealloc
{
  [_stamp release];
  [super dealloc];
}

- (void)setStamp:(id<STStamp>)stamp {
  if (_stamp) {
    [_stamp release];
  }
  _stamp = [stamp retain];
}

- (void)reloadStampedData {
  if (self.stamp) {
    [[STStampedAPI sharedInstance] stampForStampID:self.stamp.stampID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
      self.stamp = stamp;
    }];
  }
}

@end

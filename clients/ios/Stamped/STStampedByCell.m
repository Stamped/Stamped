//
//  STStampedByCell.m
//  Stamped
//
//  Created by Landon Judkins on 5/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedByCell.h"

@implementation STStampedByCell

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
  if (self) {
    
  }
  return self;
}

+ (CGFloat)cellHeightForStamp:(id<STStamp>)stamp {
  
}

+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
  
}

@end

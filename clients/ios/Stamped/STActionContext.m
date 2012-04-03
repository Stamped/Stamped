//
//  STActionContext.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionContext.h"
#import "Util.h"

@implementation STActionContext

@synthesize entityDetail = _entityDetail;
@synthesize frame = _frame;
@synthesize stamp = _stamp;

- (void)dealloc
{
  [_entityDetail release];
  [_stamp release];
  [super dealloc];
}

+ (STActionContext*)context {
  return [[[STActionContext alloc] init] autorelease];
}

+ (STActionContext*)contextInView:(UIView*)view {
  STActionContext* context = [STActionContext context];
  context.frame = [Util getAbsoluteFrame:view];
  return context;
}

@end

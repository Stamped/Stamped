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
@synthesize entity = _entity;
@synthesize frame = _frame;
@synthesize stamp = _stamp;
@synthesize user = _user;
@synthesize completionBlock = _completionBlock;
@synthesize creditedUsers = _creditedUsers;

- (void)dealloc
{
    [_entityDetail release];
    [_stamp release];
    [_user release];
    [_completionBlock release];
    [_creditedUsers release];
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

+ (STActionContext*)contextWithCompletionBlock:(void(^)(id,NSError*))block {
    STActionContext* context = [STActionContext context];
    context.completionBlock = block;
    return context;
}

@end

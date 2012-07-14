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
@synthesize controller = _controller;
@synthesize entity = _entity;
@synthesize frame = _frame;
@synthesize stamp = _stamp;
@synthesize user = _user;
@synthesize completionBlock = _completionBlock;
@synthesize creditedUsers = _creditedUsers;
@synthesize playlistItem = _playlistItem;

- (void)dealloc
{
    [_entityDetail release];
    [_stamp release];
    [_user release];
    [_completionBlock release];
    [_playlistItem release];
    [_creditedUsers release];
    [_controller release];
    [super dealloc];
}

+ (STActionContext*)context {
    return [[[STActionContext alloc] init] autorelease];
}

+ (STActionContext*)contextViewController:(UIViewController*)controller {
    STActionContext* context = [STActionContext context];
    context.controller = controller;
    return context;
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

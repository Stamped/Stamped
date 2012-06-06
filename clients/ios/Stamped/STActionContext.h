//
//  STActionContext.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"
#import "STUser.h"

@interface STActionContext : NSObject

@property (nonatomic, readwrite, retain) id<STEntityDetail> entityDetail;
@property (nonatomic, readwrite, retain) id<STEntity> entity;
@property (nonatomic, readwrite, retain) id<STStamp> stamp;
@property (nonatomic, readwrite, assign) CGRect frame;
@property (nonatomic, readwrite, retain) id<STUser> user;
@property (nonatomic, readwrite, copy) void(^completionBlock)(id,NSError*);

+ (STActionContext*)context;
+ (STActionContext*)contextInView:(UIView*)view;
+ (STActionContext*)contextWithCompletionBlock:(void(^)(id,NSError*))block;

@end

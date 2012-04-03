//
//  STActionContext.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"
#import "Stamp.h"

@interface STActionContext : NSObject

@property (nonatomic, readwrite, retain) id<STEntityDetail> entityDetail;
@property (nonatomic, readwrite, retain) Stamp* stamp;
@property (nonatomic, readwrite, assign) CGRect frame;

+ (STActionContext*)context;
+ (STActionContext*)contextInView:(UIView*)view;

@end

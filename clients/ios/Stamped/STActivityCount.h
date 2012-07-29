//
//  STActivityCount.h
//  Stamped
//
//  Created by Landon Judkins on 5/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"

@protocol STActivityCount <NSObject>

@property (nonatomic, readonly, copy) NSNumber* numberUnread;
@property (nonatomic, readonly, retain) id<STAction> action;

@end

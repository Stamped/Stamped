//
//  STActionItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"

@protocol STActionItem <NSObject>

@property (nonatomic, readonly, retain) NSString* icon;
@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, retain) id<STAction> action;

@end

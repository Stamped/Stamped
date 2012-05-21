//
//  STSimpleActionItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STActionItem.h"

@interface STSimpleActionItem : NSObject <STActionItem, NSCoding>

@property (nonatomic, readwrite, retain) NSString* icon;
@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, retain) id<STAction> action;

+ (RKObjectMapping*)mapping;

@end

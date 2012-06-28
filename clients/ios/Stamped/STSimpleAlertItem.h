//
//  STSimpleAlertItem.h
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STAlertItem.h"

@interface STSimpleAlertItem : NSObject <STAlertItem, NSCoding>

@property (nonatomic, readwrite, copy) NSString* groupID;
@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSArray<STAlertToggle>* toggles;

+ (RKObjectMapping*)mapping;

@end

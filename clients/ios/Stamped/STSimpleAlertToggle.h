//
//  STSimpleAlertToggle.h
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STAlertToggle.h"

@interface STSimpleAlertToggle : NSObject <STAlertToggle, NSCoding>

@property (nonatomic, readwrite, copy) NSString* toggleID;
@property (nonatomic, readwrite, copy) NSString* type;
@property (nonatomic, readwrite, copy) NSNumber* value;

+ (RKObjectMapping*)mapping;

@end

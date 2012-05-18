//
//  STSimpleMetadataItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STMetadataItem.h"

@interface STSimpleMetadataItem : NSObject<STMetadataItem, NSCoding>

@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, retain) NSString* value;
@property (nonatomic, readwrite, retain) NSString* icon;
@property (nonatomic, readwrite, retain) NSString* link;
@property (nonatomic, readwrite, retain) id<STAction> action;

+ (RKObjectMapping*)mapping;

@end

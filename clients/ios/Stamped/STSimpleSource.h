//
//  STSimpleSource.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STSource.h"

@interface STSimpleSource : NSObject<STSource>

@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, retain) NSString* source;
@property (nonatomic, readwrite, retain) NSString* sourceID;
@property (nonatomic, readwrite, retain) NSString* link;
@property (nonatomic, readwrite, retain) NSString* icon;

+ (RKObjectMapping*)mapping;
+ (STSimpleSource*)sourceWithSource:(NSString*)source andSourceID:(NSString*)sourceID;

@end

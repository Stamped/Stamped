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

@interface STSimpleSource : NSObject<STSource, NSCoding>

@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSString* source;
@property (nonatomic, readwrite, copy) NSDictionary* sourceData;
@property (nonatomic, readwrite, copy) NSString* sourceID;
@property (nonatomic, readwrite, copy) NSString* link;
@property (nonatomic, readwrite, copy) NSString* icon;
@property (nonatomic, readwrite, copy) NSString* endpoint;
@property (nonatomic, readwrite, copy) NSDictionary* endpointData;
@property (nonatomic, readwrite, copy) NSString* completionEndpoint;
@property (nonatomic, readwrite, copy) NSDictionary* completionData;

+ (RKObjectMapping*)mapping;
+ (STSimpleSource*)sourceWithSource:(NSString*)source andSourceID:(NSString*)sourceID;

@end

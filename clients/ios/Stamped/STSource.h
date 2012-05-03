//
//  STActionItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STSource <NSObject>

@property (nonatomic, readonly, copy) NSString* name;
@property (nonatomic, readonly, copy) NSString* source;
@property (nonatomic, readonly, copy) NSDictionary* sourceData;
@property (nonatomic, readonly, copy) NSString* sourceID;
@property (nonatomic, readonly, copy) NSString* link;
@property (nonatomic, readonly, copy) NSString* icon;
@property (nonatomic, readonly, copy) NSString* endpoint;
@property (nonatomic, readonly, copy) NSDictionary* endpointData;
@property (nonatomic, readonly, copy) NSString* completionEndpoint;
@property (nonatomic, readonly, copy) NSDictionary* completionData;

@end

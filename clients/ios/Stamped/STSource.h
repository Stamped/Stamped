//
//  STActionItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STSource <NSObject>

@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, retain) NSString* source;
@property (nonatomic, readonly, retain) NSString* sourceID;
@property (nonatomic, readonly, retain) NSString* link;
@property (nonatomic, readonly, retain) NSString* icon;
//Endpoint

@end

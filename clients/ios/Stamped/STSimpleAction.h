//
//  STSimpleAction.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STAction.h"

@interface STSimpleAction : NSObject<STAction, NSCoding>

@property (nonatomic, readwrite, retain) NSString* type;
@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, retain) NSArray<STSource>* sources;

+ (STSimpleAction*)actionWithType:(NSString*)type andSource:(id<STSource>)source;
+ (STSimpleAction*)actionWithURLString:(NSString*)url;
+ (RKObjectMapping*)mapping;

@end

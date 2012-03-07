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

@interface STSimpleAction : NSObject<STAction>

@property (nonatomic, readwrite, retain) NSString* action;
@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, retain) NSString* icon;
@property (nonatomic, readwrite, retain) NSArray<STSource>* sources;

+ (RKObjectMapping*)mapping;

@end

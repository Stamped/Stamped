//
//  STSimpleTodoSource.h
//  Stamped
//
//  Created by Landon Judkins on 5/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STTodoSource.h"

@interface STSimpleTodoSource : NSObject <STTodoSource, NSCoding>

@property (nonatomic, readwrite, retain) id<STEntity> entity;
@property (nonatomic, readwrite, copy) NSArray* stampIDs;

+ (RKObjectMapping*)mapping;

@end

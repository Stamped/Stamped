//
//  STSimpleTodo.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STTodo.h"

@interface STSimpleTodo : NSObject <STTodo, NSCoding>

@property (nonatomic, readwrite, copy) NSString* todoID;
@property (nonatomic, readwrite, copy) NSString* userID;
@property (nonatomic, readwrite, retain) id<STEntity> entity;
@property (nonatomic, readwrite, retain) id<STStamp> stamp;
@property (nonatomic, readwrite, copy) NSString* created;
@property (nonatomic, readwrite, copy) NSNumber* complete;

+ (RKObjectMapping*)mapping;

@end

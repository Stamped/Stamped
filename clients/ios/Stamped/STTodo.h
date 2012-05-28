//
//  STTodo.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTodoSource.h"
#import "STUser.h"
#import "STPreviews.h"
#import "STEntity.h"

@protocol STTodo <NSObject>

@property (nonatomic, readonly, copy) NSString* todoID;
@property (nonatomic, readonly, copy) NSString* userID;

@property (nonatomic, readonly, retain) id<STTodoSource> source;
@property (nonatomic, readonly, copy) NSDate* created;
@property (nonatomic, readonly, copy) NSNumber* complete;
@property (nonatomic, readonly, copy) NSString* stampID;

@property (nonatomic, readonly, retain) id<STPreviews> previews;

//TODO remove
@property (nonatomic, readonly, retain) id<STEntity> entity;

@end

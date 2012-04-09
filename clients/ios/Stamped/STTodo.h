//
//  STTodo.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntity.h"
#import "STStamp.h"

@protocol STTodo <NSObject>

@property (nonatomic, readonly, copy) NSString* todoID;
@property (nonatomic, readonly, copy) NSString* userID;
@property (nonatomic, readonly, retain) id<STEntity> entity;
@property (nonatomic, readonly, retain) id<STStamp> stamp;
@property (nonatomic, readonly, copy) NSString* created;
@property (nonatomic, readonly, copy) NSNumber* complete;

@end

//
//  STTodoSource.h
//  Stamped
//
//  Created by Landon Judkins on 5/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntity.h"

@protocol STTodoSource <NSObject>

@property (nonatomic, readonly, retain) id<STEntity> entity;
@property (nonatomic, readonly, copy) NSArray* stampIDs;

@end

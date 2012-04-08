//
//  STStampButton.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STToolbarButton.h"
#import "STStamp.h"
#import "STEntity.h"

@interface STStampButton : STToolbarButton

- (id)initWithStamp:(id<STStamp>)stamp;
- (id)initWithEntity:(id<STEntity>)entity;

@end

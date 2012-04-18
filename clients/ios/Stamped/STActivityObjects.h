//
//  STActivityObjects.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStamp.h"
#import "STUser.h"
#import "STEntity.h"
#import "STComment.h"

@protocol STActivityObjects <NSObject>

@property (nonatomic, readonly, copy) NSArray<STStamp> stamps;
@property (nonatomic, readonly, copy) NSArray<STEntity> entities;
@property (nonatomic, readonly, copy) NSArray<STUser> users;
@property (nonatomic, readonly, copy) NSArray<STComment> comments;

@end

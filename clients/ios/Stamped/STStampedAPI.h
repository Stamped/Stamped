//
//  STStampedAPI.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntity.h"
#import "STEntityDetail.h"
#import "STStamp.h"
#import "STUser.h"
#import "STComment.h"
#import "STCommentSlice.h"
#import "STMenu.h"

@interface STStampedAPI : NSObject

- (void)stampForStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>))block;

- (void)entityForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntity>))block;

- (void)entityDetailForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntityDetail>))block;

- (void)entityDetailForSearchID:(NSString*)searchID andCallback:(void(^)(id<STEntityDetail>))block;

- (void)userForUserID:(NSString*)userID andCallback:(void(^)(id<STUser>))block;

- (void)commentsForSlice:(STCommentSlice*)slice andCallback:(void(^)(NSArray<STComment>*))block;

- (void)menuForEntityID:(NSString*)entityID andCallback:(void(^)(id<STMenu>))block;

+ (STStampedAPI*)sharedInstance;

@end

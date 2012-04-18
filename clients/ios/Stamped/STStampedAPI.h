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
#import "STGenericCollectionSlice.h"
#import "STUserCollectionSlice.h"
#import "STFriendsSlice.h"
#import "STCommentSlice.h"
#import "STMenu.h"
#import "STTodo.h"
#import "STStampedBySlice.h"
#import "STUserDetail.h"
#import "STStampedBy.h"


typedef enum {
  STStampedAPIScopeYou = 0,
  STStampedAPIScopeFriends,
  STStampedAPIScopeFriendsOfFriends,
  STStampedAPIScopeEveryone
} STStampedAPIScope;

@interface STStampedAPI : NSObject

//TODO modifify calls to returns cancellable NSOperations that have already been disbatched and autoreleased
// This strategy should be reverse compatible with existing usage.

//TODO upgrade all deprecated error-less methods

- (id<STUser>)currentUser;

- (void)stampForStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>))block;

- (void)stampsForInboxSlice:(STGenericCollectionSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block;

- (void)stampsForUserSlice:(STUserCollectionSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block;

- (void)stampsForFriendsSlice:(STFriendsSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block;

- (void)stampsForSuggestedSlice:(STGenericCollectionSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block;

- (void)stampedByForStampedBySlice:(STStampedBySlice*)slice andCallback:(void(^)(id<STStampedBy>, NSError*))block;

- (void)deleteStampWithStampID:(NSString*)stampID andCallback:(void(^)(BOOL,NSError*))block;

- (void)entityForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntity>))block;

- (void)entityDetailForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntityDetail> detail, NSError* error))block;

- (void)entityDetailForSearchID:(NSString*)searchID andCallback:(void(^)(id<STEntityDetail>))block;

- (void)userDetailForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block;

- (void)commentsForSlice:(STCommentSlice*)slice andCallback:(void(^)(NSArray<STComment>*,NSError*))block;

- (void)createCommentForStampID:(NSString*)stampID 
                      withBlurb:(NSString*)blurb 
                    andCallback:(void(^)(id<STComment> comment, NSError* error))block;

- (void)menuForEntityID:(NSString*)entityID andCallback:(void(^)(id<STMenu>))block;

- (void)likeWithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block;

- (void)unlikeWithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block;

- (void)todoWithStampID:(NSString*)stampID 
               entityID:(NSString*)entityID 
            andCallback:(void(^)(id<STTodo>,NSError*))block;

- (void)untodoWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block;

- (void)isTododWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block;

- (void)todosWithGenericCollectionSlice:(STGenericCollectionSlice*)slice 
                            andCallback:(void(^)(NSArray<STTodo>*,NSError*))block;

+ (STStampedAPI*)sharedInstance;

@end

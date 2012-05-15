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
#import "STEntitySuggested.h"
#import "STSimpleEntitySearchResult.h"
#import "STEntitySearch.h"
#import "STEntitySearchResult.h"
#import "STEntitySearchSection.h"
#import "STActivity.h"
#import "STStampNew.h"
#import "STCancellation.h"
#import "STTypes.h"
#import "STActionContext.h"
#import "STLazyList.h"
#import "STConsumptionSlice.h"
#import "STActivityCount.h"

typedef enum {
  STStampedAPIScopeYou = 0,
  STStampedAPIScopeFriends,
  STStampedAPIScopeFriendsOfFriends,
  STStampedAPIScopeEveryone
} STStampedAPIScope;

typedef enum {
  STStampedAPIErrorUnavailable,
} STStampedAPIError;

@interface STStampedAPI : NSObject

//TODO modifify calls to returns cancellable NSOperations that have already been disbatched and autoreleased
// This strategy should be reverse compatible with existing usage.

//TODO upgrade all deprecated error-less methods

+ (NSString*)errorDomain;

- (id<STUser>)currentUser;

- (id<STLazyList>)globalListByScope:(STStampedAPIScope)scope;

- (id<STStamp>)cachedStampForStampID:(NSString*)stampID;

- (STCancellation*)stampForStampID:(NSString*)stampID 
                       andCallback:(void(^)(id<STStamp> stamp, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForInboxSlice:(STGenericCollectionSlice*)slice 
                           andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForUserSlice:(STUserCollectionSlice*)slice 
                          andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForFriendsSlice:(STFriendsSlice*)slice 
                             andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForSuggestedSlice:(STGenericCollectionSlice*)slice 
                               andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForConsumptionSlice:(STConsumptionSlice*)slice 
                                 andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampedByForStampedBySlice:(STStampedBySlice*)slice 
                                  andCallback:(void(^)(id<STStampedBy> stampedBy, NSError* error, STCancellation* cancellation))block;

- (void)createStampWithStampNew:(STStampNew*)stampNew andCallback:(void(^)(id<STStamp> stamp, NSError* error))block;

- (void)deleteStampWithStampID:(NSString*)stampID andCallback:(void(^)(BOOL,NSError*))block;

- (STCancellation*)entityForEntityID:(NSString*)entityID 
                         andCallback:(void(^)(id<STEntity> entity, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entityDetailForEntityID:(NSString*)entityID 
                               andCallback:(void(^)(id<STEntityDetail> detail, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entityResultsForEntitySuggested:(STEntitySuggested*)entitySuggested 
                                       andCallback:(void(^)(NSArray<STEntitySearchSection>* sections, NSError* error, STCancellation* cancellation))block;

- (void)entityResultsForEntitySearch:(STEntitySearch*)entitySearch 
                         andCallback:(void(^)(NSArray<STEntitySearchResult>* results, NSError* error))block;

- (void)entityDetailForSearchID:(NSString*)searchID andCallback:(void(^)(id<STEntityDetail>))block;

- (void)activitiesForYouWithGenericSlice:(STGenericSlice*)slice 
                             andCallback:(void(^)(NSArray<STActivity>* activities, NSError* error))block;

- (void)activitiesForFriendsWithGenericSlice:(STGenericSlice*)slice 
                                 andCallback:(void(^)(NSArray<STActivity>* activities, NSError* error))block;

- (void)userDetailForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block;

- (STCancellation*)userDetailsForUserIDs:(NSArray*)userIDs 
                             andCallback:(void(^)(NSArray<STUserDetail>* userDetails, NSError* error, STCancellation* cancellation))block;

- (void)isFriendForUserID:(NSString*)userID andCallback:(void(^)(BOOL isFriend, NSError* error))block;

- (void)commentsForSlice:(STCommentSlice*)slice andCallback:(void(^)(NSArray<STComment>*,NSError*))block;

- (STCancellation*)createCommentForStampID:(NSString*)stampID 
                                 withBlurb:(NSString*)blurb 
                               andCallback:(void(^)(id<STComment> comment, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)menuForEntityID:(NSString*)entityID 
                       andCallback:(void(^)(id<STMenu> menu, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)likeWithStampID:(NSString*)stampID 
                       andCallback:(void(^)(id<STStamp>, NSError*, STCancellation*))block;

- (STCancellation*)unlikeWithStampID:(NSString*)stampID 
                         andCallback:(void(^)(id<STStamp>,NSError*, STCancellation*))block;

- (STCancellation*)todoWithStampID:(NSString*)stampID 
                          entityID:(NSString*)entityID 
                       andCallback:(void(^)(id<STTodo>,NSError*,STCancellation*))block;

- (STCancellation*)untodoWithStampID:(NSString*)stampID 
                            entityID:(NSString*)entityID
                         andCallback:(void(^)(BOOL,NSError*,STCancellation*))block;

- (void)isTododWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block;

- (void)todosWithGenericCollectionSlice:(STGenericCollectionSlice*)slice 
                            andCallback:(void(^)(NSArray<STTodo>*,NSError*))block;

- (void)followerIDsForUserID:(NSString*)userID andCallback:(void(^)(NSArray* followerIDs, NSError* error))block;

- (void)addFriendForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block;

- (void)removeFriendForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block;

- (void)friendIDsForUserID:(NSString*)userID andCallback:(void(^)(NSArray* friendIDs, NSError* error))block;

- (void)handleCompletionWithSource:(id<STSource>)source action:(NSString*)action andContext:(STActionContext*)context;

- (STCancellation*)unreadCountWithCallback:(void(^)(id<STActivityCount> count, NSError* error, STCancellation* cancellation))block;

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;

- (NSString*)stringForScope:(STStampedAPIScope)scope;

- (void)fastPurge;

+ (STStampedAPI*)sharedInstance;

@end

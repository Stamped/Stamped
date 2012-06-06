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
#import "STLoginResponse.h"
#import "STEntityAutoCompleteResult.h"
#import "STHybridCacheSource.h"

typedef enum {
    STStampedAPIScopeYou = 0,
    STStampedAPIScopeFriends,
    STStampedAPIScopeEveryone,
    STStampedAPIScopeFriendsOfFriends,
} STStampedAPIScope;

typedef enum {
    STStampedAPIErrorUnavailable,
} STStampedAPIError;

extern NSString* const STStampedAPILoginNotification;
extern NSString* const STStampedAPILogoutNotification;
extern NSString* const STStampedAPIUserUpdatedNotification;

@interface STStampedAPI : NSObject

//TODO modifify calls to returns cancellable NSOperations that have already been disbatched and autoreleased
// This strategy should be reverse compatible with existing usage.

//TODO upgrade all deprecated error-less methods

+ (NSString*)errorDomain;

- (id<STUser>)currentUser;

- (id<STLazyList>)globalListByScope:(STStampedAPIScope)scope;

- (id<STStamp>)cachedStampForStampID:(NSString*)stampID;

- (void)cacheStamp:(id<STStamp>)stamp;

- (id<STPreviews>)cachedPreviewsForStampID:(NSString*)stampID;

- (void)cachePreviews:(id<STPreviews>)previews forStampID:(NSString*)stampID;

- (id<STStampedBy>)cachedStampedByForEntityID:(NSString*)entityID;

- (id<STUser>)cachedUserForUserID:(NSString*)userID;

- (void)cacheUser:(id<STUser>)user;

- (id<STEntity>)cachedEntityForEntityID:(NSString*)entityID;

- (void)cacheEntity:(id<STEntity>)entity;

- (STCancellation*)stampedByForEntityID:(NSString*)entityID
                            andCallback:(void(^)(id<STStampedBy> stampedBy, NSError* error, STCancellation* cancellation))block;

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

- (STCancellation*)createStampWithStampNew:(STStampNew*)stampNew 
                               andCallback:(void(^)(id<STStamp> stamp, NSError* error, STCancellation* cancellation))block;

- (void)deleteStampWithStampID:(NSString*)stampID andCallback:(void(^)(BOOL,NSError*))block;

- (STCancellation*)entityDetailForEntityID:(NSString*)entityID
                               andCallback:(void(^)(id<STEntityDetail> detail, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entityDetailForEntityID:(NSString*)entityID
                               forceUpdate:(BOOL)forceUpdate
                               andCallback:(void(^)(id<STEntityDetail> detail, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entityResultsForEntitySuggested:(STEntitySuggested*)entitySuggested 
                                       andCallback:(void(^)(NSArray<STEntitySearchSection>* sections, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entityResultsForEntitySearch:(STEntitySearch*)entitySearch 
                                    andCallback:(void(^)(NSArray<STEntitySearchSection>* sections, NSError* error, STCancellation* cancellation))block;

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

- (STCancellation*)entityAutocompleteResultsForQuery:(NSString*)query 
                                         coordinates:(NSString*)coordinates
                                            category:(NSString*)category
                                         andCallback:(void(^)(NSArray<STEntityAutoCompleteResult>* results, NSError* error, STCancellation* cancellation))block;

- (void)isTododWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block;

- (STCancellation*)todosWithGenericCollectionSlice:(STGenericCollectionSlice*)slice 
                                       andCallback:(void(^)(NSArray<STTodo>* todos, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsWithScope:(STStampedAPIScope)scope
                              date:(NSDate*)date 
                             limit:(NSInteger)limit 
                            offset:(NSInteger)offset
                       andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsWithUserID:(NSString*)userID
                               date:(NSDate*)date 
                              limit:(NSInteger)limit 
                             offset:(NSInteger)offset
                        andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entitiesWithScope:(STStampedAPIScope)scope 
                             section:(NSString*)section
                          subsection:(NSString*)subsection 
                               limit:(NSNumber*)limit
                              offset:(NSNumber*)offset 
                         andCallback:(void(^)(NSArray<STEntityDetail>* entities, NSError* error, STCancellation* cancellation))block;

- (void)followerIDsForUserID:(NSString*)userID andCallback:(void(^)(NSArray* followerIDs, NSError* error))block;

- (void)addFriendForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block;

- (void)removeFriendForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block;

- (void)friendIDsForUserID:(NSString*)userID andCallback:(void(^)(NSArray* friendIDs, NSError* error))block;

- (void)handleCompletionWithSource:(id<STSource>)source action:(NSString*)action andContext:(STActionContext*)context;

- (STCancellation*)unreadCountWithCallback:(void(^)(id<STActivityCount> count, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loginWithScreenName:(NSString*)screenName 
                              password:(NSString*)password 
                           andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loginWithFacebookUserToken:(NSString*)userToken
                                  andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loginWithTwitterUserToken:(NSString*)userToken 
                                  userSecret:(NSString*)userSecret
                                 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithPassword:(NSString*)password
                                  screenName:(NSString*)screenName
                                        name:(NSString*)name
                                       email:(NSString*)email
                                       phone:(NSString*)phone //optional
                                profileImage:(NSString*)profileImage //optional
                                 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithFacebookUserToken:(NSString*)userToken 
                                           screenName:(NSString*)screenName
                                                 name:(NSString*)name
                                                email:(NSString*)email //optional
                                                phone:(NSString*)phone //optional
                                         profileImage:(NSString*)profileImage //optional
                                          andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithTwitterUserToken:(NSString*)userToken 
                                          userSecret:(NSString*)userSecret
                                          screenName:(NSString*)screenName
                                                name:(NSString*)name
                                               email:(NSString*)email //optional
                                               phone:(NSString*)phone //optional
                                        profileImage:(NSString*)profileImage //optional
                                         andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;

- (NSString*)stringForScope:(STStampedAPIScope)scope;

- (void)fastPurge;

+ (STStampedAPI*)sharedInstance;

@end

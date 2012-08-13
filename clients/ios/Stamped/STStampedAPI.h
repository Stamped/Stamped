//
//  STStampedAPI.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 The client interface to StampedAPI
 
 Before I describe anything about StampedAPI, it's important to
 understand the data model system that it uses. API return types
 (define by interface in the Protocol group and defined by implementation
 in the Simple Models group)
 
 This class encapsulates the majority of Stamped API calls with an
 implementation agnostic interface. In general, methods are presented
 as asynchronous, cancellable, callback-based methods. Internally, 
 this class maps these methods into REST API calls with parameter and
 result conversion/unpacking as necessary. In addition to hiding the
 networking details of the implementation, this class also provides
 substantial caching, notification, and local modification systems.
 Currently, the following data structures are cached:
 
 entityDetails
 stamps
 users
 entities
 stampedBy
 menus
 stampPreviews
 
 The exact rules of caching are beyond the scope of this comment.
 The local modification system is also a bit complex to describe here, but
 in short, things like comments and likes are added locally to new copies of
 models (in this case stamps) and the new object replaces the old one in the cache.
 Notifications are posted for a number of actions. See the notification
 declarations for more info (the names are fairly self-explanatory).
 
 Notes:
 This class has become quite large. At time of writing, this
 class has the second longest implementation of any file in the project*.
 
 TODOs:
 Make methods consistent (all cancellable, standard callback format, naming, etc.)
 Reduce import statements
 
 2012-08-10
 -Landon 
 
 *Util is the largest.
 
 */

#import <Foundation/Foundation.h>
#import "STEntity.h"
#import "STEntityDetail.h"
#import "STStamp.h"
#import "STUser.h"
#import "STComment.h"
#import "STGenericCollectionSlice.h"
#import "STUserCollectionSlice.h"
#import "STFriendsSlice.h"
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
#import "STAccountParameters.h"
#import "STRestKitLoader.h"
#import "STAccount.h"
#import <CoreLocation/CoreLocation.h>
#import "STAlertItem.h"
#import "STLinkedAccounts.h"
#import "STCache.h"

#define LOGGED_IN ([[STStampedAPI sharedInstance] currentUser] != nil)
#define IS_CURRENT_USER(user_id) [[[[STStampedAPI sharedInstance] currentUser] userID] isEqualToString:(user_id)]

typedef enum {
    STStampedAPIErrorUnavailable,
} STStampedAPIError;

extern NSString* const STStampedAPILoginNotification;
extern NSString* const STStampedAPILogoutNotification;
extern NSString* const STStampedAPIRefreshedTokenNotification;
extern NSString* const STStampedAPIUserUpdatedNotification;
extern NSString* const STStampedAPILocalStampModificationNotification;
extern NSString* const STStampedAPILocalTodoModificationNotification;
extern NSString* const STStampedAPIFollowNotification;
extern NSString* const STStampedAPIUnfollowNotification;

@interface STStampedAPI : NSObject <STCacheAccelerator>

//TODO modifify calls to returns cancellable NSOperations that have already been disbatched and autoreleased
// This strategy should be reverse compatible with existing usage.

//TODO upgrade all deprecated error-less methods

+ (NSString*)errorDomain;

- (id<STUserDetail>)currentUser;

@property (readwrite, retain) CLLocation* currentUserLocation;

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

- (STCancellation*)stampForStampID:(NSString*)stampID 
                       forceUpdate:(BOOL)forceUpdate
                       andCallback:(void(^)(id<STStamp> stamp, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForInboxSlice:(STGenericCollectionSlice*)slice 
                           andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForUserSlice:(STUserCollectionSlice*)slice 
                          andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForFriendsSlice:(STFriendsSlice*)slice 
                             andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)stampsForSuggestedSlice:(STGenericCollectionSlice*)slice 
                               andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entitiesForConsumptionSlice:(STConsumptionSlice*)slice 
                                   andCallback:(void(^)(NSArray<STEntityDetail>* entities, NSError* error, STCancellation* cancellation))block;

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

- (STCancellation*)entityDetailForSearchID:(NSString*)searchID 
                               andCallback:(void(^)(id<STEntityDetail>, NSError*, STCancellation*))block;

- (STCancellation*)activitiesForScope:(STStampedAPIScope)scope
                               offset:(NSInteger)offset 
                                limit:(NSInteger)limit 
                          andCallback:(void(^)(NSArray<STActivity>* activities, NSError* error, STCancellation* cancellation))block;

- (void)userDetailForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block;

- (STCancellation*)userDetailForScreenName:(NSString*)screenName 
                               andCallback:(void (^)(id<STUserDetail> userDetail, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)userDetailsForUserIDs:(NSArray*)userIDs 
                             andCallback:(void(^)(NSArray<STUserDetail>* userDetails, NSError* error, STCancellation* cancellation))block;

- (void)isFriendForUserID:(NSString*)userID andCallback:(void(^)(BOOL isFriend, NSError* error))block;

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

- (STCancellation*)setTodoCompleteWithEntityID:(NSString*)entityID 
                                      complete:(BOOL)complete
                                   andCallback:(void(^)(id<STTodo> todo, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)entityAutocompleteResultsForQuery:(NSString*)query 
                                         coordinates:(NSString*)coordinates
                                            category:(NSString*)category
                                         andCallback:(void(^)(NSArray<STEntityAutoCompleteResult>* results, NSError* error, STCancellation* cancellation))block;

- (void)isTododWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block;

- (STCancellation*)todosWithGenericCollectionSlice:(STGenericCollectionSlice*)slice 
                                       andCallback:(void(^)(NSArray<STTodo>* todos, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)todosWithDate:(NSDate*)date 
                           limit:(NSInteger)limit 
                          offset:(NSInteger)offset
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
                           accountParameters:(STAccountParameters*)accountParameters
                                 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithFacebookUserToken:(NSString*)userToken 
                                    accountParameters:(STAccountParameters*)accountParameters
                                          andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithTwitterUserToken:(NSString*)userToken 
                                          userSecret:(NSString*)userSecret 
                                   accountParameters:(STAccountParameters*)accountParameters
                                         andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)registerAPNSToken:(NSString*)token 
                         andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createLogWithKey:(NSString*)key 
                              value:(NSString*)value 
                            stampID:(NSString*)stampID
                           entityID:(NSString*)entityID
                             todoID:(NSString*)todoID
                          commentID:(NSString*)commentID 
                         activityID:(NSString*)activityID
                        andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;


- (STCancellation*)accountWithCallback:(void (^)(id<STAccount> account, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)updateAccountWithAccountParameters:(STAccountParameters*)accountParameters 
                                          andCallback:(void (^)(id<STUserDetail> user, NSError* error, STCancellation* cancellation))block;

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;

- (STCancellation*)alertsWithCallback:(void (^)(NSArray<STAlertItem>* alerts, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)creditingStampsWithUserID:(NSString*)userID 
                                        date:(NSDate*)date 
                                       limit:(NSInteger)limit 
                                      offset:(NSInteger)offset
                                 andCallback:(void (^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)alertsWithOnIDs:(NSArray*)onIDs
                            offIDs:(NSArray*)offIDS 
                       andCallback:(void (^)(NSArray<STAlertItem>* alerts, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)shareSettingsWithService:(NSString*)service
                                andCallback:(void (^)(NSArray<STAlertItem>* alerts, NSError* error, STCancellation* cancellation))block;


- (STCancellation*)linkedAccountsWithCallback:(void (^)(id<STLinkedAccounts> linkedAccounts, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)removeLinkedAccountWithService:(NSString*)service
                                      andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (NSString*)stringForScope:(STStampedAPIScope)scope;

- (void)fastPurge;

+ (STStampedAPI*)sharedInstance;

- (UIImage*)currentUserImageForSize:(STProfileImageSize)profileImageSize;

- (STCancellation*)createEntityWithParams:(NSDictionary*)params
                              andCallback:(void (^)(id<STEntityDetail> entityDetail, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)usersWithEmails:(NSArray*)emails 
                       andCallback:(void (^)(NSArray<STUserDetail>* users, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)usersWithPhoneNumbers:(NSArray*)phoneNumbers 
                             andCallback:(void (^)(NSArray<STUserDetail>* users, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)deleteAccountWithCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)usersFromFacebookWithCallback:(void (^)(NSArray<STUserDetail>* users, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)usersFromTwitterWithCallback:(void (^)(NSArray<STUserDetail>* users, NSError* error, STCancellation* cancellation))block;

+ (void)logError:(NSString*)message;

@property (nonatomic, readwrite, retain) UIImage* currentUserImage;

@end


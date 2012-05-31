//
//  STStampedAPI.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedAPI.h"
#import "STMenuFactory.h"
#import "STEntityDetailFactory.h"
#import "Util.h"
#import "STCacheModelSource.h"
#import "STRestKitLoader.h"
#import "STSimpleStamp.h"
#import "STSimpleTodo.h"
#import "STSimpleComment.h"
#import "STSimpleUser.h"
#import "AccountManager.h"
#import "STSimpleUserDetail.h"
#import "STSimpleStampedBy.h"
#import "STSimpleEntitySearchResult.h"
#import "STSimpleEntitySearchSection.h"
#import "STSimpleActivity.h"
#import "STSimpleEntityDetail.h"
#import "STDebug.h"
#import "STYouStampsList.h"
#import "STFriendsStampsList.h"
#import "STFriendsOfFriendsStampsList.h"
#import "STEveryoneStampsList.h"
#import "STSimpleEndpointResponse.h"
#import "STActionManager.h"
#import "STSimpleActivityCount.h"
#import "STSimplePreviews.h"
#import "STPersistentCacheSource.h"
#import "STSimpleMenu.h"
#import "STHybridCacheSource.h"
#import "STSimpleLoginResponse.h"
#import "STSimpleEntityAutoCompleteResult.h"

@interface STStampedAPIUserIDs : NSObject

@property (nonatomic, readwrite, copy) NSArray* userIDs;

+ (RKObjectMapping*)mapping;

@end

@implementation STStampedAPIUserIDs

@synthesize userIDs = userIDs_;

- (void)dealloc
{
    [userIDs_ release];
    [super dealloc];
}

+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STStampedAPIUserIDs class]];
    [mapping mapKeyPath:@"user_ids" toAttribute:@"userIDs"];
    return mapping;
}

@end

@interface STStampedAPI () <STCacheModelSourceDelegate, STPersistentCacheSourceDelegate, STHybridCacheSourceDelegate>

@property (nonatomic, readonly, retain) STPersistentCacheSource* menuCache;
@property (nonatomic, readonly, retain) STHybridCacheSource* stampCache;
@property (nonatomic, readonly, retain) STHybridCacheSource* entityDetailCache;
@property (nonatomic, readonly, retain) STHybridCacheSource* stampedByCache;
@property (nonatomic, readonly, retain) NSCache* stampPreviewsCache;
@property (nonatomic, readonly, retain) NSCache* userCache;
@property (nonatomic, readonly, retain) NSCache* entityCache;
@property (nonatomic, readwrite, retain) id<STActivityCount> lastCount;

- (void)path:(NSString*)path WithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block;

@end

@implementation STStampedAPI

@synthesize menuCache = _menuCache;
@synthesize stampCache = _stampCache;
@synthesize entityDetailCache = entityDetailCache_;
@synthesize stampedByCache = _stampedByCache;
@synthesize stampPreviewsCache = _stampPreviewsCache;
@synthesize lastCount = lastCount_;
@synthesize userCache = _userCache;
@synthesize entityCache = _entityCache;

static STStampedAPI* _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STStampedAPI alloc] init];
}

+ (STStampedAPI*)sharedInstance {
    return _sharedInstance;
}

+ (NSString *)errorDomain {
    return @"STStampedAPI";
}

- (id)init
{
    self = [super init];
    if (self) {
        _menuCache = [[STPersistentCacheSource alloc] initWithDelegate:self andDirectoryPath:@"Menus" relativeToCacheDir:YES];
        _stampCache = [[STHybridCacheSource alloc] initWithCachePath:@"Stamps" relativeToCacheDir:YES];
        _stampCache.delegate = self;
        entityDetailCache_ = [[STHybridCacheSource alloc] initWithCachePath:@"Entities" relativeToCacheDir:YES];
        entityDetailCache_.delegate = self;
        entityDetailCache_.maxMemoryCost = 20;
        entityDetailCache_.maxAge = [NSNumber numberWithInteger:60];
        _stampedByCache = [[STHybridCacheSource alloc] initWithCachePath:@"StampedBy" relativeToCacheDir:YES];
        _stampedByCache.delegate = self;
        _stampedByCache.maxAge = [NSNumber numberWithInteger:1 * 24 * 60 * 60];
        _stampPreviewsCache =[[NSCache alloc] init];
        _userCache = [[NSCache alloc] init];
        _entityCache = [[NSCache alloc] init];
    }
    return self;
}

- (void)dealloc
{
    _menuCache.delegate = nil;
    _stampCache.delegate = nil;
    entityDetailCache_.delegate = nil;
    _stampedByCache.delegate = nil;
    [_menuCache release];
    [_stampCache release];
    [_stampedByCache release];
    [_stampPreviewsCache release];
    [_userCache release];
    [_entityCache release];
    [entityDetailCache_ release];
    [lastCount_ release];
    [super dealloc];
}

- (id<STUser>)cachedUserForUserID:(NSString*)userID {
    return [self.userCache objectForKey:userID];
}

- (void)cacheUser:(id<STUser>)user {
    [self.userCache setObject:user forKey:user.userID];
}

- (id<STEntity>)cachedEntityForEntityID:(NSString*)entityID {
    return [self.entityCache objectForKey:entityID];
}

- (void)cacheEntity:(id<STEntity>)entity {
    [self.entityCache setObject:entity forKey:entity.entityID];
}

- (id<STUser>)currentUser {
    return [STSimpleUser userFromLegacyUser:[AccountManager sharedManager].currentUser];
}

- (id<STStamp>)cachedStampForStampID:(NSString*)stampID {
    return (id<STStamp>)[self.stampCache fastCachedObjectForKey:stampID];
}

- (void)cacheStamp:(id<STStamp>)stamp {
    [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
}

- (id<STPreviews>)cachedPreviewsForStampID:(NSString*)stampID {
    return [self.stampPreviewsCache objectForKey:stampID];
}

- (void)cachePreviews:(id<STPreviews>)previews forStampID:(NSString*)stampID {
    return [self.stampPreviewsCache setObject:previews forKey:stampID];
}

- (id<STStampedBy>)cachedStampedByForEntityID:(NSString*)entityID {
    return (id)[self.stampedByCache fastCachedObjectForKey:entityID];
}

- (STCancellation*)stampForStampID:(NSString*)stampID 
                       andCallback:(void(^)(id<STStamp> stamp, NSError* error, STCancellation* cancellation))block {
    NSAssert(stampID != nil,@"stampID must not be nil");
    return [self.stampCache objectForKey:stampID forceUpdate:NO cacheAfterCancel:NO withCallback:^(id<NSCoding> model, NSError *error, STCancellation *cancellation) {
        block((id)model, error, cancellation);
    }];
}


- (STCancellation*)stampsForSlice:(STGenericSlice*)slice 
                         withPath:(NSString*)path 
                      andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    NSDictionary* params = [slice asDictionaryParams];
    void(^outerBlock)(NSArray*,NSError*, STCancellation*) = ^(NSArray* stamps, NSError* error, STCancellation* cancellation) {
        NSMutableArray<STStamp>* array = [NSMutableArray array]; 
        if (stamps) {
            for (id<STStamp> stamp in stamps) {
                if (stamp.deleted.boolValue) {
                    [self.stampCache removeObjectForKey:stamp.stampID];
                }
                else {
                    [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
                    [array addObject:stamp];
                }
            }
            block(array, error, cancellation);
        }
        else {
            block(nil, error, cancellation);
        }
        
    };
    return [[STRestKitLoader sharedInstance] loadWithPath:path 
                                                     post:NO 
                                                   params:params 
                                                  mapping:[STSimpleStamp mapping] 
                                              andCallback:outerBlock];
    
}

- (STCancellation*)stampsForInboxSlice:(STGenericCollectionSlice*)slice 
                           andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [self stampsForSlice:slice withPath:@"/collections/inbox.json" andCallback:block];
}

- (STCancellation*)stampsForUserSlice:(STUserCollectionSlice*)slice 
                          andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [self stampsForSlice:slice withPath:@"/collections/user.json" andCallback:block];
}

- (STCancellation*)stampsForFriendsSlice:(STFriendsSlice*)slice 
                             andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [self stampsForSlice:slice withPath:@"/collections/friends.json" andCallback:block];
}

- (STCancellation*)stampsForSuggestedSlice:(STGenericCollectionSlice*)slice 
                               andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [self stampsForSlice:slice withPath:@"/collections/suggested.json" andCallback:block];
}

- (STCancellation*)stampsForConsumptionSlice:(STConsumptionSlice*)slice 
                                 andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [self stampsForSlice:slice withPath:@"/collections/consumption.json" andCallback:block];
}

- (STCancellation*)stampedByForStampedBySlice:(STStampedBySlice*)slice 
                                  andCallback:(void(^)(id<STStampedBy> stampedBy, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/entities/stamped_by.json";
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                        post:NO 
                                                      params:[slice asDictionaryParams] 
                                                     mapping:[STSimpleStampedBy mapping]
                                                 andCallback:^(id stampedBy, NSError* error, STCancellation* cancellation) {
                                                     block(stampedBy, block, cancellation);
                                                 }];
}

- (STCancellation*)createStampWithStampNew:(STStampNew*)stampNew 
                               andCallback:(void(^)(id<STStamp>, NSError*, STCancellation*))block {
    NSString* path = @"/stamps/create.json";
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                                      params:stampNew.asDictionaryParams
                                                     mapping:[STSimpleStamp mapping]
                                                 andCallback:^(id stamp, NSError* error, STCancellation* cancellation) {
                                                     block(stamp, error, cancellation);
                                                 }];
}

- (void)deleteStampWithStampID:(NSString*)stampID andCallback:(void(^)(BOOL,NSError*))block {
    NSString* path = @"/stamps/remove.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                 post:YES 
                                               params:params 
                                              mapping:[STSimpleStamp mapping]
                                          andCallback:^(id stamp, NSError* error, STCancellation* cancellation) {
                                              if (stamp) {
                                                  [[self globalListByScope:STStampedAPIScopeYou] reload];
                                                  [[self globalListByScope:STStampedAPIScopeFriends] reload];
                                                  [self.stampCache removeObjectForKey:stampID];
                                              }
                                              block(stamp != nil, error);
                                          }];
}

- (STCancellation*)entityResultsForEntitySuggested:(STEntitySuggested*)entitySuggested 
                                       andCallback:(void(^)(NSArray<STEntitySearchSection>*, NSError*, STCancellation*))block {
    NSString* path = @"/entities/suggested.json";
    return [[STRestKitLoader sharedInstance] loadWithPath:path 
                                                     post:NO 
                                                   params:entitySuggested.asDictionaryParams 
                                                  mapping:[STSimpleEntitySearchSection mapping] 
                                              andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                                                  block((NSArray<STEntitySearchSection>*)array, error, cancellation);
                                              }];
}

- (STCancellation*)entityResultsForEntitySearch:(STEntitySearch*)entitySearch 
                                    andCallback:(void(^)(NSArray<STEntitySearchSection>* sections, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/entities/search.json";
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                                   params:entitySearch.asDictionaryParams
                                                  mapping:[STSimpleEntitySearchSection mapping]
                                              andCallback:^(NSArray* result, NSError *error, STCancellation *cancellation) {
                                                  block((id)result, error, cancellation); 
                                              }];
}

- (void)userDetailForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block {
    NSString* path = @"/users/show.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                 post:NO 
                                               params:params 
                                              mapping:[STSimpleUserDetail mapping]
                                          andCallback:^(id user, NSError* error, STCancellation* cancellation) {
                                              block(user, error);
                                          }];
}

- (STCancellation*)userDetailsForUserIDs:(NSArray*)userIDs 
                             andCallback:(void(^)(NSArray<STUserDetail>*, NSError*, STCancellation*))block {
    NSString* path = @"/users/lookup.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:[userIDs componentsJoinedByString:@","] forKey:@"user_ids"];
    return [[STRestKitLoader sharedInstance] loadWithPath:path 
                                                     post:YES 
                                                   params:params 
                                                  mapping:[STSimpleUserDetail mapping]
                                              andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                                                  block((NSArray<STUserDetail>*)array, error, cancellation);
                                              }];
}

- (STCancellation*)entityDetailForEntityID:(NSString*)entityID 
                               andCallback:(void(^)(id<STEntityDetail>, NSError*, STCancellation*))block {
    return [self entityDetailForEntityID:entityID forceUpdate:NO andCallback:block];
}

- (STCancellation*)entityDetailForEntityID:(NSString*)entityID
                               forceUpdate:(BOOL)forceUpdate
                               andCallback:(void(^)(id<STEntityDetail> detail, NSError* error, STCancellation* cancellation))block {
    return [self.entityDetailCache objectForKey:entityID 
                                    forceUpdate:forceUpdate 
                               cacheAfterCancel:NO 
                                   withCallback:^(id<NSCoding> model, NSError *error, STCancellation *cancellation) {
                                       block((id<STEntityDetail>)model, error, cancellation);
                                   }];
}

- (void)entityDetailForSearchID:(NSString*)searchID andCallback:(void(^)(id<STEntityDetail>))block{
    NSOperation* operation = [[STEntityDetailFactory sharedFactory] entityDetailCreatorWithSearchId:searchID andCallbackBlock:block];
    [Util runOperationAsynchronously:operation];
}

- (void)activitiesForYouWithGenericSlice:(STGenericSlice*)slice 
                             andCallback:(void(^)(NSArray<STActivity>* activities, NSError* error))block {
    NSString* path = @"/activity/show.json";
    self.lastCount = nil;
    [[STRestKitLoader sharedInstance] loadWithPath:path 
                                              post:NO
                                            params:slice.asDictionaryParams
                                           mapping:[STSimpleActivity mapping]
                                       andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                                           block((NSArray<STActivity>*)array, error);
                                       }];
}

- (void)activitiesForFriendsWithGenericSlice:(STGenericSlice*)slice 
                                 andCallback:(void(^)(NSArray<STActivity>* activities, NSError* error))block {
    NSString* path = @"/activity/friends.json";
    
    [[STRestKitLoader sharedInstance] loadWithPath:path 
                                              post:NO
                                            params:slice.asDictionaryParams
                                           mapping:[STSimpleActivity mapping]
                                       andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                                           block((NSArray<STActivity>*)array, error);
                                       }];
}

- (STCancellation*)menuForEntityID:(NSString*)entityID 
                       andCallback:(void(^)(id<STMenu> menu, NSError* error, STCancellation* cancellation))block {
    return [self.menuCache fetchWithKey:entityID callback:block];
}

- (void)commentsForSlice:(STCommentSlice*)slice andCallback:(void(^)(NSArray<STComment>*,NSError*))block {
    //TODO
}

- (void)_updateLocalStampWithStampID:(NSString*)stampID 
                                todo:(id<STUser>)todo
                                like:(id<STUser>)like
                             comment:(id<STComment>)comment
                           andCredit:(id<STStamp>)credit{
    id<STStamp> stamp = [self cachedStampForStampID:stampID];
    if (stamp) {
        STSimpleStamp* copy = [STSimpleStamp augmentedStampWithStamp:stamp todo:todo like:like comment:comment andCredit:credit];
        [self.stampCache setObject:copy forKey:stampID];
    }
}

- (void)_reduceLocalStampWithStampID:(NSString*)stampID 
                                todo:(id<STUser>)todo
                                like:(id<STUser>)like
                             comment:(id<STComment>)comment
                           andCredit:(id<STStamp>)credit{
    id<STStamp> stamp = [self cachedStampForStampID:stampID];
    if (stamp) {
        STSimpleStamp* copy = [STSimpleStamp reducedStampWithStamp:stamp todo:todo like:like comment:comment andCredit:credit];
        [self.stampCache setObject:copy forKey:stampID];
    }
}

- (STCancellation*)createCommentForStampID:(NSString*)stampID 
                                 withBlurb:(NSString*)blurb 
                               andCallback:(void(^)(id<STComment>, NSError*, STCancellation*))block {
    NSString* path = @"/comments/create.json";
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                            stampID, @"stamp_id",
                            blurb, @"blurb",
                            nil];
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                        post:YES 
                                                      params:params 
                                                     mapping:[STSimpleComment mapping] 
                                                 andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                                     if (!error && result) {
                                                         [self _updateLocalStampWithStampID:stampID
                                                                                       todo:nil
                                                                                       like:nil
                                                                                    comment:result
                                                                                  andCredit:nil];
                                                     }
                                                     block(result, error, cancellation);
                                                 }];
}

- (STCancellation*)likeWithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>, NSError*, STCancellation*))block {
    NSString* path = @"/stamps/likes/create.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                                      params:params
                                                     mapping:[STSimpleStamp mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     if (!error && result) {
                                                         [self _updateLocalStampWithStampID:stampID
                                                                                       todo:nil
                                                                                       like:[self currentUser]
                                                                                    comment:nil
                                                                                  andCredit:nil];
                                                     }
                                                     block(result, error, cancellation);
                                                 }];
}

- (STCancellation*)unlikeWithStampID:(NSString*)stampID 
                         andCallback:(void(^)(id<STStamp>, NSError*, STCancellation*))block {
    NSString* path = @"/stamps/likes/remove.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                                      params:params
                                                     mapping:[STSimpleStamp mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     if (!error && result) {
                                                         [self _reduceLocalStampWithStampID:stampID
                                                                                       todo:nil
                                                                                       like:[self currentUser]
                                                                                    comment:nil
                                                                                  andCredit:nil];
                                                     }
                                                     block(result, error, cancellation);
                                                 }];
}

- (STCancellation*)todoWithStampID:(NSString*)stampID 
                          entityID:(NSString*)entityID 
                       andCallback:(void(^)(id<STTodo>,NSError*,STCancellation*))block {
    NSString* path = @"/todos/create.json";
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                            stampID, @"stamp_id",
                            entityID, @"entity_id",
                            nil];
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                        post:YES 
                                                      params:params 
                                                     mapping:[STSimpleTodo mapping] 
                                                 andCallback:^(id todo, NSError* error, STCancellation* cancellation) {
                                                     if (todo && !error) {
                                                         [self _updateLocalStampWithStampID:stampID
                                                                                       todo:[self currentUser]
                                                                                       like:nil
                                                                                    comment:nil
                                                                                  andCredit:nil];
                                                     }
                                                     block(todo, error, cancellation);
                                                 }];
}


- (STCancellation*)todosWithGenericCollectionSlice:(STGenericCollectionSlice*)slice 
                                       andCallback:(void(^)(NSArray<STTodo>*, NSError*, STCancellation*))block {
    NSString* path = @"/todos/show.json";
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                                   params:slice.asDictionaryParams
                                                  mapping:[STSimpleTodo mapping]
                                              andCallback:^(NSArray* results, NSError* error, STCancellation* cancellation) {
                                                  block((NSArray<STTodo>*)results,error, cancellation);
                                              }];
}

- (void)isTododWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block {
    //TODO
}

- (STCancellation*)untodoWithStampID:(NSString*)stampID 
                            entityID:(NSString*)entityID
                         andCallback:(void(^)(BOOL,NSError*,STCancellation*))block {
    NSString* path = @"/favorites/remove.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:entityID forKey:@"entity_id"];
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                        post:YES 
                                                      params:params 
                                                     mapping:[STSimpleTodo mapping] 
                                                 andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                                     if (result && !error && stampID) {
                                                         [self _reduceLocalStampWithStampID:stampID 
                                                                                       todo:[self currentUser]
                                                                                       like:nil
                                                                                    comment:nil
                                                                                  andCredit:nil];
                                                     }
                                                     block(error == nil, error, cancellation);
                                                 }];
}

- (void)followerIDsForUserID:(NSString*)userID andCallback:(void(^)(NSArray* followerIDs, NSError* error))block {
    NSString* path = @"/friendships/followers.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                 post:NO
                                               params:params
                                              mapping:[STStampedAPIUserIDs mapping]
                                          andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                              STStampedAPIUserIDs* userIDs = result;
                                              block(userIDs ? userIDs.userIDs : nil, error);
                                          }];
}

- (void)friendIDsForUserID:(NSString*)userID andCallback:(void(^)(NSArray* friendIDs, NSError* error))block {
    NSString* path = @"/friendships/friends.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                 post:NO
                                               params:params
                                              mapping:[STStampedAPIUserIDs mapping]
                                          andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                              STStampedAPIUserIDs* userIDs = result;
                                              block(userIDs ? userIDs.userIDs : nil, error);
                                          }];
}

- (void)isFriendForUserID:(NSString*)userID andCallback:(void(^)(BOOL isFriend, NSError* error))block {
    NSString* path = @"/friendships/check.json";
    NSDictionary* dictionary = [NSDictionary dictionaryWithObjectsAndKeys:
                                userID, @"user_id_b", 
                                [AccountManager sharedManager].currentUser.userID, @"user_id_a",
                                nil];
    [[STRestKitLoader sharedInstance] booleanWithPath:path
                                                 post:NO
                                               params:dictionary
                                          andCallback:^(BOOL boolean, NSError *error, STCancellation* cancellation) {
                                              block(boolean, error);
                                          }];
}

- (void)addFriendForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block {
    NSString* path = @"/friendships/create.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                 post:YES
                                               params:params 
                                              mapping:[STSimpleUserDetail mapping]
                                          andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                              block(result, error);
                                          }];
}

- (void)removeFriendForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block {
    NSString* path = @"/friendships/remove.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                 post:YES
                                               params:params 
                                              mapping:[STSimpleUserDetail mapping]
                                          andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                              block(result, error);
                                          }];
}

- (void)path:(NSString*)path WithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block {
    NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                 post:YES 
                                               params:params 
                                              mapping:[STSimpleStamp mapping] 
                                          andCallback:^(id stamp, NSError* error, STCancellation* cancellation) {
                                              block(stamp, error);
                                          }];
}

- (STCancellation*)objectForPersistentCache:(STPersistentCacheSource *)cache 
                                    withKey:(NSString *)key 
                           andCurrentObject:(id)object
                               withCallback:(void (^)(id<NSCoding>, NSError *, STCancellation *))block {
    if (cache == self.menuCache) {
        STCancellation* cancellation = [STCancellation cancellation];
        [[STMenuFactory sharedFactory] menuWithEntityId:key andCallbackBlock:^(id<STMenu> menu) {
            if (!cancellation.cancelled) {
                if (menu) {
                    block((STSimpleMenu*)menu, nil, cancellation);
                }
                else {
                    block(nil, [NSError errorWithDomain:[STStampedAPI errorDomain]
                                                   code:STStampedAPIErrorUnavailable
                                               userInfo:[NSDictionary dictionaryWithObjectsAndKeys:@"key",key, nil]], cancellation);
                }
            }
        }];
        return cancellation;
    }
    return nil;
}

- (STCancellation*)objectForCache:(STCacheModelSource*)cache 
                          withKey:(NSString*)key 
                 andCurrentObject:(id)object 
                     withCallback:(void(^)(id model, NSInteger cost, NSError* error, STCancellation* cancellation))block {
    NSAssert2(NO, @"unknown cache (%@) asked for key %@", cache, key);
    return nil;
}

- (void)handleCompletionWithSource:(id<STSource>)source action:(NSString*)action andContext:(STActionContext*)context {
    
    if (source.completionEndpoint) {
        NSMutableDictionary* params = [NSMutableDictionary dictionary];
        if (source.completionData) {
            [params addEntriesFromDictionary:source.completionData];
        }
        if (context.stamp && ![params objectForKey:@"stamp_id"]) {
            [params setObject:context.stamp.stampID forKey:@"stamp_id"];
        }
        
        [[STRestKitLoader sharedInstance] booleanWithURL:source.completionEndpoint
                                                    post:YES
                                                  params:params
                                             andCallback:^(BOOL boolean, NSError *error, STCancellation *cancellation) {
                                                 [STDebug log:[NSString stringWithFormat:@"Callback %@ for endpoint %@.\n%@:%@:%@\n%@",
                                                               boolean ? @"succeeded" : @"failed",
                                                               source.completionEndpoint,
                                                               action,
                                                               source.source,
                                                               source.sourceID,
                                                               params]];
                                             }];
    }
}

- (STCancellation*)unreadCountWithCallback:(void(^)(id<STActivityCount>, NSError*, STCancellation*))block {
    id<STActivityCount> cached = self.lastCount;
    if (cached) {
        STCancellation* cancellation = [STCancellation cancellation];
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(cached, nil, cancellation);
            }
        }];
        return cancellation;
    }
    else {
        NSString* path = @"/activity/unread.json";
        return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                            post:NO
                                                          params:[NSDictionary dictionary]
                                                         mapping:[STSimpleActivityCount mapping]
                                                     andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                         if (result) {
                                                             //self.lastCount = result;
                                                         }
                                                         block(result, error, cancellation);
                                                     }];
    }
}

- (id<STLazyList>)globalListByScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        return [STYouStampsList sharedInstance];
    }
    else if (scope == STStampedAPIScopeFriends) {
        return [STFriendsStampsList sharedInstance];
    }
    else if (scope == STStampedAPIScopeFriendsOfFriends) {
        return [STFriendsOfFriendsStampsList sharedInstance];
    }
    else if (scope == STStampedAPIScopeEveryone) {
        return [STEveryoneStampsList sharedInstance];
    }
    NSAssert1(NO, @"Bad scope value: %", scope);
    return nil;
}

- (void)handleEndpointCallback:(id)result withError:(NSError*)error andCancellation:(STCancellation*)cancellation {
    if (result) {
        id<STEndpointResponse> response = result;
        if (response.action) {
            [[STActionManager sharedActionManager] didChooseAction:response.action withContext:[STActionContext context]];
        }
    }
}

- (BOOL)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context execute:(BOOL)flag {
    BOOL handled = NO;
    if (source.endpoint) {
        handled = YES;
        if (flag) {
            NSMutableDictionary* params = [NSMutableDictionary dictionary];
            if (source.endpointData) {
                [params addEntriesFromDictionary:source.endpointData];
            }
            [[STRestKitLoader sharedInstance] loadOneWithURL:source.endpoint
                                                        post:YES
                                                      params:params
                                                     mapping:[STSimpleEndpointResponse mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     if (error) {
                                                         [STDebug log:[NSString stringWithFormat:@"Callback error for action %@ and endpoint %@ with data %@",
                                                                       action, source.source, params]];
                                                     }
                                                     [self handleEndpointCallback:result withError:error andCancellation:cancellation];
                                                 }];
        }
    }
    return handled;
}

- (STCancellation *)objectForHybridCache:(STHybridCacheSource *)cache 
                                 withKey:(NSString *)key
                            withCallback:(void (^)(id<NSCoding>, NSError *, STCancellation *))block {
    if (cache == self.stampCache) {
        NSDictionary* params = [NSDictionary dictionaryWithObject:key forKey:@"stamp_id"];
        NSString* path = @"/stamps/show.json";
        return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                            post:NO 
                                                          params:params 
                                                         mapping:[STSimpleStamp mapping] 
                                                     andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                         block(result, error, cancellation);
                                                     }];
    }
    if (cache == self.entityDetailCache) {
        NSDictionary* params = [NSDictionary dictionaryWithObject:key forKey:@"entity_id"];
        NSString* path = @"/entities/show.json";
        return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                            post:NO
                                                          params:params
                                                         mapping:[STSimpleEntityDetail mapping]
                                                     andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                         block(result, error, cancellation);
                                                     }];
    }
    if (cache == self.stampedByCache) {
        NSString* path = @"/entities/stamped_by.json";
        return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                            post:NO 
                                                          params:[NSDictionary dictionaryWithObject:key forKey:@"entity_id"] 
                                                         mapping:[STSimpleStampedBy mapping]
                                                     andCallback:^(id stampedBy, NSError* error, STCancellation* cancellation) {
                                                         block(stampedBy, block, cancellation);
                                                     }];
    }
    NSAssert1(NO, @"Unknown hybrid cache %@", cache);
    return nil;
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
    return [self didChooseSource:source forAction:action withContext:context execute:NO];
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
    [self didChooseSource:source forAction:action withContext:context execute:YES];
}

- (NSString*)stringForScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        return @"me";
    }
    else if (scope == STStampedAPIScopeFriends) {
        return @"inbox";
    }
    else if (scope == STStampedAPIScopeFriendsOfFriends) {
        return @"robby";
    }
    else {
        return @"everyone";
    }
}

- (STCancellation*)loginWithFacebookID:(NSString*)userID 
                                 token:(NSString*)token
                           andCallback:(void(^)(id<STLoginResponse>, NSError*, STCancellation*))block {
    NSString* path = @"/account/create_using_facebook.json";
    NSDictionary* params = nil;
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                                      params:params
                                                     mapping:[STSimpleLoginResponse mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     block(result, error, cancellation); 
                                                 }];
}

- (STCancellation*)entityAutocompleteResultsForQuery:(NSString*)query 
                                         coordinates:(NSString*)coordinates
                                            category:(NSString*)category
                                         andCallback:(void(^)(NSArray<STEntityAutoCompleteResult>* results, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/entities/autosuggest.json";
    NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                   query, @"query",
                                   category, @"category",
                                   nil];
    if (coordinates) {
        [params setObject:coordinates forKey:@"coordinates"];
    }
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                                   params:params
                                                  mapping:[STSimpleEntityAutoCompleteResult mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  block((id)results, error, cancellation); 
                                              }];
}


- (STCancellation*)stampsWithScope:(STStampedAPIScope)scope
                              date:(NSDate*)date 
                             limit:(NSInteger)limit 
                            offset:(NSInteger)offset
                       andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/stamps/collection.json";
    NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                   [self stringForScope:scope], @"scope",
                                   [NSNumber numberWithInteger:limit], @"limit",
                                   [NSNumber numberWithInteger:[date timeIntervalSince1970]], @"before",
                                   nil];
    if (offset != 0) {
        [params setObject:[NSNumber numberWithInteger:offset] forKey:@"offset"];
    }
    if (scope == STStampedAPIScopeFriendsOfFriends) {
        [params setObject:@"4e57048accc2175fcd000001" forKey:@"user_id"];
    }
    NSAssert1(date, @"Date must not be nil for %@", self);
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                                   params:params
                                                  mapping:[STSimpleStamp mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  if (results) {
                                                      for (id<STStamp> stamp in results) {
                                                          [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
                                                      }
                                                  }
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)stampsWithUserID:(NSString*)userID
                               date:(NSDate*)date 
                              limit:(NSInteger)limit 
                             offset:(NSInteger)offset
                        andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/stamps/collection.json";
    NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                   userID, @"userID",
                                   [NSNumber numberWithInteger:limit], @"limit",
                                   [NSNumber numberWithInteger:[date timeIntervalSince1970]], @"before",
                                   nil];
    if (offset != 0) {
        [params setObject:[NSNumber numberWithInteger:offset] forKey:@"offset"];
    }
    NSAssert1(date, @"Date must not be nil for %@", self);
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                                   params:params
                                                  mapping:[STSimpleStamp mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  if (results) {
                                                      for (id<STStamp> stamp in results) {
                                                          [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
                                                      }
                                                  }
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)entitiesWithScope:(STStampedAPIScope)scope 
                             section:(NSString*)section
                          subsection:(NSString*)subsection 
                               limit:(NSNumber*)limit
                              offset:(NSNumber*)offset 
                         andCallback:(void(^)(NSArray<STEntityDetail>* entities, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/stamps/guide.json";
    NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                   [self stringForScope:scope], @"scope",
                                   section, @"section",
                                   nil];
    if (subsection) {
        [params setObject:subsection forKey:@"subsection"];
    }
    if (limit) {
        [params setObject:limit forKey:@"limit"];
    }
    if (offset) {
        [params setObject:offset forKey:@"offset"];
    }
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                                   params:params
                                                  mapping:[STSimpleEntityDetail mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)stampedByForEntityID:(NSString*)entityID
                            andCallback:(void(^)(id<STStampedBy> stampedBy, NSError* error, STCancellation* cancellation))block {
    return [self.stampedByCache objectForKey:entityID forceUpdate:NO cacheAfterCancel:NO withCallback:^(id<NSCoding> model, NSError *error, STCancellation *cancellation) {
        block((id)model, error, cancellation); 
    }];
}

- (void)fastPurge {
    [self.entityDetailCache fastMemoryPurge];
    [self.stampCache fastMemoryPurge];
    [self.stampedByCache fastMemoryPurge];
    [self.userCache removeAllObjects];
    //[self.menuCache purge];
}

@end

//
//  STStampedAPI.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedAPI.h"
#import "Util.h"
#import "STRestKitLoader.h"
#import "STSimpleStamp.h"
#import "STSimpleTodo.h"
#import "STSimpleComment.h"
#import "STSimpleUser.h"
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
#import "STSimpleBooleanResponse.h"
#import "STSimpleAccount.h"
#import "STImageCache.h"
#import "STSimpleAlertItem.h"
#import "STSimpleLinkedAccounts.h"

NSString* const STStampedAPILoginNotification = @"STStampedAPILoginNotification";
NSString* const STStampedAPILogoutNotification = @"STStampedAPILogoutNotification";
NSString* const STStampedAPIUserUpdatedNotification = @"STStampedAPIUserUpdatedNotification";
NSString* const STStampedAPILocalStampModificationNotification = @"STStampedAPILocalStampModification";
NSString* const STStampedAPIRefreshedTokenNotification = @"STStampedAPIRefreshTokenNotification";

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

@interface STStampedAPI () <STPersistentCacheSourceDelegate, STHybridCacheSourceDelegate>


@property (nonatomic, readonly, retain) STPersistentCacheSource* menuCache;
@property (nonatomic, readonly, retain) STHybridCacheSource* stampCache;
@property (nonatomic, readonly, retain) STHybridCacheSource* entityDetailCache;
@property (nonatomic, readonly, retain) STHybridCacheSource* stampedByCache;
@property (nonatomic, readwrite, retain) STCancellation* userImageCancellation;
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
@synthesize currentUserLocation = _currentUserLocation;
@synthesize currentUserImage = _currentUserImage;
@synthesize userImageCancellation = _userImageCancellation;

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
        entityDetailCache_.maxAge = [NSNumber numberWithInteger:7 * 24 * 60 * 60];
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
    [_userImageCancellation cancel];
    [_userImageCancellation release];
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)_didLogout:(id)notImportant {
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

- (id<STUserDetail>)currentUser {
    return [[STRestKitLoader sharedInstance] currentUser];
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
    return [self stampForStampID:stampID forceUpdate:NO andCallback:block];
}

- (STCancellation*)stampForStampID:(NSString*)stampID 
                       forceUpdate:(BOOL)forceUpdate
                       andCallback:(void(^)(id<STStamp> stamp, NSError* error, STCancellation* cancellation))block {
    NSAssert(stampID != nil,@"stampID must not be nil");
    return [self.stampCache objectForKey:stampID 
                             forceUpdate:forceUpdate 
                        cacheAfterCancel:NO 
                            withCallback:^(id<NSCoding> model, NSError *error, STCancellation *cancellation) {
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
                [self.stampedByCache removeObjectForKey:stamp.entity.entityID];
            }
            block(array, error, cancellation);
        }
        else {
            block(nil, error, cancellation);
        }
        
    };
    return [[STRestKitLoader sharedInstance] loadWithPath:path 
                                                     post:NO
                                            authenticated:YES
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
    return [self stampsForSlice:slice withPath:@"/stamps/collection.json" andCallback:block];
}

- (STCancellation*)stampsForFriendsSlice:(STFriendsSlice*)slice 
                             andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [self stampsForSlice:slice withPath:@"/collections/friends.json" andCallback:block];
}

- (STCancellation*)stampsForSuggestedSlice:(STGenericCollectionSlice*)slice 
                               andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [self stampsForSlice:slice withPath:@"/collections/suggested.json" andCallback:block];
}

- (STCancellation*)entitiesForConsumptionSlice:(STConsumptionSlice*)slice 
                                   andCallback:(void(^)(NSArray<STEntityDetail>* entities, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/guide/collection.json";
    NSMutableDictionary* params = slice.asDictionaryParams;
    if ([params objectForKey:@"category"]) {
        [params setObject:[params objectForKey:@"category"] forKey:@"section"];
        [params removeObjectForKey:@"category"];
    }
    if ([params objectForKey:@"subcategory"]) {
        [params setObject:[params objectForKey:@"subcategory"] forKey:@"subsection"];
        [params removeObjectForKey:@"subcategory"];
    }
    
    if ([params objectForKey:@"query"]) {
        path = @"/guide/search.json";
    }
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleEntityDetail mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)createStampWithStampNew:(STStampNew*)stampNew 
                               andCallback:(void(^)(id<STStamp>, NSError*, STCancellation*))block {
    NSString* path = @"/stamps/create.json";
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                               authenticated:YES
                                                      params:stampNew.asDictionaryParams
                                                     mapping:[STSimpleStamp mapping]
                                                 andCallback:^(id stamp, NSError* error, STCancellation* cancellation) {
                                                     if (stamp) {
                                                         [self.stampedByCache removeObjectForKey:[stamp entity].entityID];
                                                         [self.stampCache setObject:stamp forKey:[stamp stampID]];
                                                         [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPILocalStampModificationNotification
                                                                                                             object:[stamp stampID]];
                                                     }
                                                     block(stamp, error, cancellation);
                                                 }];
}

- (void)deleteStampWithStampID:(NSString*)stampID andCallback:(void(^)(BOOL,NSError*))block {
    NSString* path = @"/stamps/remove.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                 post:YES 
                                        authenticated:YES
                                               params:params 
                                              mapping:[STSimpleStamp mapping]
                                          andCallback:^(id stamp, NSError* error, STCancellation* cancellation) {
                                              if (stamp) {
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
                                            authenticated:YES
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
                                            authenticated:YES
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
                                        authenticated:YES
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
                                            authenticated:YES
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

- (STCancellation*)entityDetailForSearchID:(NSString*)searchID 
                               andCallback:(void(^)(id<STEntityDetail>, NSError*, STCancellation*))block {
    NSString* path = @"/entities/show.json";
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:NO
                                               authenticated:YES
                                                      params:[NSDictionary dictionaryWithObject:searchID forKey:@"entity_id"]
                                                     mapping:[STSimpleEntityDetail mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     if (result) {
                                                         [self.entityDetailCache setObject:result forKey:[result entityID]];
                                                     }
                                                     block(result, error, cancellation);
                                                 }];
}

- (STCancellation*)activitiesForScope:(STStampedAPIScope)scope
                               offset:(NSInteger)offset 
                                limit:(NSInteger)limit 
                          andCallback:(void(^)(NSArray<STActivity>* activities, NSError* error, STCancellation* cancellation))block {
    NSMutableDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                                   scope == STStampedAPIScopeYou ? @"me" : @"friends", @"scope",
                                   [NSNumber numberWithInteger:offset], @"offset",
                                   [NSNumber numberWithInteger:limit], @"limit",
                                   nil];
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/activity/collection.json"
                                                     post:NO
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleActivity mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  
                                                  if (results) {
                                                      for (id<STActivity> activity in results) {
                                                          if (activity.objects.stamps.count > 0) {
                                                              for (id<STStamp> stamp in activity.objects.stamps) {
                                                                  [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
                                                                  [self.stampedByCache removeObjectForKey:stamp.entity.entityID];
                                                              }
                                                          }
                                                      }
                                                  }
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)menuForEntityID:(NSString*)entityID 
                       andCallback:(void(^)(id<STMenu> menu, NSError* error, STCancellation* cancellation))block {
    return [self.menuCache fetchWithKey:entityID callback:block];
}

- (void)_updateLocalStampWithStampID:(NSString*)stampID 
                                todo:(id<STUser>)todo
                                like:(id<STUser>)like
                             comment:(id<STComment>)comment
                           andCredit:(id<STStamp>)credit{
    id<STStamp> stamp = [self cachedStampForStampID:stampID];
    void (^block)(id<STStamp> stamp) = ^(id<STStamp> stamp) {
        STSimpleStamp* copy = [STSimpleStamp augmentedStampWithStamp:stamp todo:todo like:like comment:comment andCredit:credit];
        [self.stampCache setObject:copy forKey:stampID];
        [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPILocalStampModificationNotification object:stampID];
    };
    if (stamp) {
        block(stamp);
    }
    else {
        [self stampForStampID:stampID andCallback:^(id<STStamp> stamp, NSError *error, STCancellation *cancellation) {
            if (stamp) {
                block(stamp);
            }
        }];
    }
}

- (void)_reduceLocalStampWithStampID:(NSString*)stampID 
                                todo:(id<STUser>)todo
                                like:(id<STUser>)like
                             comment:(id<STComment>)comment
                           andCredit:(id<STStamp>)credit{
    id<STStamp> stamp = [self cachedStampForStampID:stampID];
    void (^block)(id<STStamp> stamp) = ^(id<STStamp> stamp) {
        STSimpleStamp* copy = [STSimpleStamp reducedStampWithStamp:stamp todo:todo like:like comment:comment andCredit:credit];
        [self.stampCache setObject:copy forKey:stampID];
        [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPILocalStampModificationNotification object:stampID];
    };
    if (stamp) {
        block(stamp);
    }
    else {
        [self stampForStampID:stampID andCallback:^(id<STStamp> stamp, NSError *error, STCancellation *cancellation) {
            if (stamp) {
                block(stamp);
            }
        }];
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
    if (![Util isOffline]) {
        STSimpleComment* comment = [STSimpleComment commentWithBlurb:blurb user:self.currentUser andStampID:stampID];
        [Util executeOnMainThread:^{
            [self _updateLocalStampWithStampID:stampID
                                          todo:nil
                                          like:nil
                                       comment:comment
                                     andCredit:nil];
        }];
    }
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                        post:YES 
                                               authenticated:YES
                                                      params:params 
                                                     mapping:[STSimpleComment mapping] 
                                                 andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                                     block(result, error, cancellation);
                                                 }];
}

- (STCancellation*)likeWithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>, NSError*, STCancellation*))block {
    NSString* path = @"/stamps/likes/create.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
    if (![Util isOffline]) {
        [Util executeOnMainThread:^{
            [self _updateLocalStampWithStampID:stampID
                                          todo:nil
                                          like:[self currentUser]
                                       comment:nil
                                     andCredit:nil];
        }];
    }
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                               authenticated:YES
                                                      params:params
                                                     mapping:[STSimpleStamp mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     block(result, error, cancellation);
                                                 }];
}

- (STCancellation*)unlikeWithStampID:(NSString*)stampID 
                         andCallback:(void(^)(id<STStamp>, NSError*, STCancellation*))block {
    NSString* path = @"/stamps/likes/remove.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
    if (![Util isOffline]) { 
        id<STUser> currentUser = self.currentUser;
        [Util executeOnMainThread:^ {
            [self _reduceLocalStampWithStampID:stampID
                                          todo:nil
                                          like:currentUser
                                       comment:nil
                                     andCredit:nil];
        }];
    }
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                               authenticated:YES
                                                      params:params
                                                     mapping:[STSimpleStamp mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     block(result, error, cancellation);
                                                 }];
}

- (STCancellation*)todoWithStampID:(NSString*)stampID 
                          entityID:(NSString*)entityID 
                       andCallback:(void(^)(id<STTodo>,NSError*,STCancellation*))block {
    NSString* path = @"/todos/create.json";
    NSMutableDictionary* params = [NSMutableDictionary dictionary];
    if (stampID) {
        [params setObject:stampID forKey:@"stamp_id"];
    }
    if (entityID) {
        [params setObject:entityID forKey:@"entity_id"];
    }
    if (![Util isOffline] && stampID) { 
        id<STUser> currentUser = self.currentUser;
        [Util executeOnMainThread:^ {
            [self _updateLocalStampWithStampID:stampID
                                          todo:currentUser
                                          like:nil
                                       comment:nil
                                     andCredit:nil];
        }];
    }
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                        post:YES 
                                               authenticated:YES
                                                      params:params 
                                                     mapping:[STSimpleTodo mapping] 
                                                 andCallback:^(id todo, NSError* error, STCancellation* cancellation) {
                                                     block(todo, error, cancellation);
                                                 }];
}


- (STCancellation*)todosWithGenericCollectionSlice:(STGenericCollectionSlice*)slice 
                                       andCallback:(void(^)(NSArray<STTodo>*, NSError*, STCancellation*))block {
    NSString* path = @"/todos/collection.json";
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                            authenticated:YES
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
    NSString* path = @"/todos/remove.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:entityID forKey:@"entity_id"];
    if (![Util isOffline]) { 
        id<STUser> currentUser = self.currentUser;
        [Util executeOnMainThread:^ {
            [self _reduceLocalStampWithStampID:stampID 
                                          todo:currentUser
                                          like:nil
                                       comment:nil
                                     andCredit:nil];
            
        }];
    }
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                        post:YES 
                                               authenticated:YES
                                                      params:params 
                                                     mapping:[STSimpleTodo mapping] 
                                                 andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                                     block(error == nil, error, cancellation);
                                                 }];
}

- (STCancellation*)setTodoCompleteWithEntityID:(NSString*)entityID 
                                      complete:(BOOL)complete
                                   andCallback:(void(^)(id<STTodo>,NSError*,STCancellation*))block {
    NSString* path = @"/todos/complete.json";
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                            entityID, @"entity_id",
                            [NSNumber numberWithBool:complete], @"complete",
                            nil];
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:YES
                                               authenticated:YES
                                                      params:params
                                                     mapping:[STSimpleTodo mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     block(result, error, cancellation);
                                                 }];
}

- (void)followerIDsForUserID:(NSString*)userID andCallback:(void(^)(NSArray* followerIDs, NSError* error))block {
    NSString* path = @"/friendships/followers.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                 post:NO
                                        authenticated:YES
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
                                        authenticated:YES
                                               params:params
                                              mapping:[STStampedAPIUserIDs mapping]
                                          andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                              STStampedAPIUserIDs* userIDs = result;
                                              block(userIDs ? userIDs.userIDs : nil, error);
                                          }];
}

- (void)isFriendForUserID:(NSString*)userID andCallback:(void(^)(BOOL isFriend, NSError* error))block {
    NSString* currentUserID = self.currentUser.userID;
    if (currentUserID) {
        NSString* path = @"/friendships/check.json";
        NSDictionary* dictionary = [NSDictionary dictionaryWithObjectsAndKeys:
                                    userID, @"user_id_b", 
                                    currentUserID, @"user_id_a",
                                    nil];
        [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                     post:NO
                                            authenticated:YES
                                                   params:dictionary 
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id<STBooleanResponse> response, NSError *error, STCancellation* cancellation) {
                                                  if (response) {
                                                      block(response.result.boolValue, nil);
                                                  }
                                                  else {
                                                      block(NO, error);
                                                  }
                                              }];
    }
    else {
        [Util executeOnMainThread:^{
            block(NO, [NSError errorWithDomain:@"StampedAPI" code:0 userInfo:[NSDictionary dictionaryWithObject:@"not logged in" forKey:@"Reason"]]); 
        }];
    }
}

- (void)addFriendForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block {
    NSString* path = @"/friendships/create.json";
    NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                 post:YES
                                        authenticated:YES
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
                                        authenticated:YES
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
                                        authenticated:YES
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
        return [[STRestKitLoader sharedInstance] loadOneWithPath:@"/entities/menu.json"
                                                            post:NO
                                                   authenticated:YES
                                                          params:[NSDictionary dictionaryWithObject:key forKey:@"entity_id"]
                                                         mapping:[STSimpleMenu mapping]
                                                     andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                         block(result, error, cancellation);
                                                     }];
    }
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
        [[STRestKitLoader sharedInstance] loadOneWithPath:[NSString stringWithFormat:@"/%@", source.completionEndpoint]
                                                     post:YES
                                            authenticated:YES
                                                   params:params 
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                  
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
                                                   authenticated:YES
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
            [[STRestKitLoader sharedInstance] loadOneWithPath:[NSString stringWithFormat:@"/%@", source.endpoint]
                                                         post:YES
                                                authenticated:YES
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
    NSAssert1(key, @"Key should not be none for cache %@", cache);
    if (key == nil) {
        return nil;
    }
    if (cache == self.stampCache) {
        NSDictionary* params = [NSDictionary dictionaryWithObject:key forKey:@"stamp_id"];
        NSString* path = @"/stamps/show.json";
        return [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                                            post:NO 
                                                   authenticated:YES
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
                                                   authenticated:YES
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
                                                   authenticated:YES
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
        return @"user";
    }
    else {
        return @"popular";
    }
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
                                            authenticated:YES
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
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleStamp mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  if (results) {
                                                      for (id<STStamp> stamp in results) {
                                                          [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
                                                          [self.stampedByCache removeObjectForKey:stamp.entity.entityID];
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
                                   userID, @"user_id",
                                   [NSNumber numberWithInteger:limit], @"limit",
                                   [NSNumber numberWithInteger:[date timeIntervalSince1970]], @"before",
                                   @"user", @"scope",
                                   nil];
    if (offset != 0) {
        [params setObject:[NSNumber numberWithInteger:offset] forKey:@"offset"];
    }
    NSAssert1(date, @"Date must not be nil for %@", self);
    return [[STRestKitLoader sharedInstance] loadWithPath:path
                                                     post:NO
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleStamp mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  if (results) {
                                                      for (id<STStamp> stamp in results) {
                                                          [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
                                                          [self.stampedByCache removeObjectForKey:stamp.entity.entityID];
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
    NSString* path = @"/guide/collection.json";
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
                                            authenticated:YES
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

- (STCancellation *)createAccountWithPassword:(NSString *)password 
                            accountParameters:(STAccountParameters*)accountParameters
                                  andCallback:(void (^)(id<STLoginResponse>, NSError *, STCancellation *))block {
    return [[STRestKitLoader sharedInstance] createAccountWithPassword:password 
                                                     accountParameters:accountParameters
                                                           andCallback:block];
}

- (STCancellation*)createAccountWithFacebookUserToken:(NSString*)userToken 
                                    accountParameters:(STAccountParameters*)accountParameters
                                          andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] createAccountWithFacebookUserToken:userToken
                                                              accountParameters:accountParameters
                                                                    andCallback:block];
}

- (STCancellation *)createAccountWithTwitterUserToken:(NSString *)userToken 
                                           userSecret:(NSString *)userSecret 
                                    accountParameters:(STAccountParameters*)accountParameters
                                          andCallback:(void (^)(id<STLoginResponse>, NSError *, STCancellation *))block {
    return [[STRestKitLoader sharedInstance] createAccountWithTwitterUserToken:userToken
                                                                    userSecret:userSecret
                                                             accountParameters:accountParameters
                                                                   andCallback:block];
}


- (STCancellation*)loginWithScreenName:(NSString*)screenName 
                              password:(NSString*)password 
                           andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loginWithScreenName:screenName password:password andCallback:block];
}

- (STCancellation *)loginWithFacebookUserToken:(NSString *)userToken
                                   andCallback:(void (^)(id<STLoginResponse>, NSError *, STCancellation *))block {
    return [[STRestKitLoader sharedInstance] loginWithFacebookUserToken:userToken andCallback:block];
}

- (STCancellation *)loginWithTwitterUserToken:(NSString *)userToken
                                   userSecret:(NSString *)userSecret
                                  andCallback:(void (^)(id<STLoginResponse>, NSError *, STCancellation *))block {
    return [[STRestKitLoader sharedInstance] loginWithTwitterUserToken:userToken
                                                            userSecret:userSecret
                                                           andCallback:block];
}

- (STCancellation*)registerAPNSToken:(NSString*)token 
                         andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/alerts/ios/update.json"
                                                        post:YES
                                               authenticated:YES
                                                      params:[NSDictionary dictionaryWithObject:token forKey:@"token"]
                                                     mapping:[STSimpleUser mapping] //TODO fix
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     block(YES, error, cancellation); 
                                                 }];
}

- (STCancellation*)createLogWithKey:(NSString*)key 
                              value:(NSString*)value 
                            stampID:(NSString*)stampID
                           entityID:(NSString*)entityID
                             todoID:(NSString*)todoID
                          commentID:(NSString*)commentID 
                         activityID:(NSString*)activityID
                        andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    NSMutableDictionary* params = [NSMutableDictionary dictionary];
    if (key) {
        [params setObject:key forKey:@"key"];
    }
    if (value) {
        [params setObject:value forKey:@"value"];
    }
    if (stampID) {
        [params setObject:stampID forKey:@"stamp_id"];
    }
    if (entityID) {
        [params setObject:entityID forKey:@"entity_id"];
    }
    if (todoID) {
        [params setObject:todoID forKey:@"todo_id"];
    }
    if (commentID) {
        [params setObject:commentID forKey:@"comment_id"];
    }
    if (activityID) {
        [params setObject:activityID forKey:@"activity_id"];
    }
    return [[STRestKitLoader sharedInstance] loadOneWithPath:@"/private/logs/create.json"
                                                        post:YES
                                               authenticated:YES
                                                      params:params
                                                     mapping:[STSimpleBooleanResponse mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     if (result) {
                                                         block(YES, nil, cancellation);
                                                     }
                                                     else {
                                                         block(NO, error, cancellation);
                                                     }
                                                 }];
}


- (STCancellation*)accountWithCallback:(void (^)(id<STAccount> account, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/show.json"
                                                        post:NO
                                               authenticated:YES
                                                      params:[NSDictionary dictionary]
                                                     mapping:[STSimpleAccount mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     block(result, error, cancellation); 
                                                 }];
}

- (STCancellation*)updateAccountWithAccountParameters:(STAccountParameters*)accountParameters 
                                          andCallback:(void (^)(id<STUserDetail> user, NSError* error, STCancellation* cancellation))block {
    
    return [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/update.json"
                                                        post:YES
                                               authenticated:YES
                                                      params:accountParameters.asDictionaryParams
                                                     mapping:[STSimpleUserDetail mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     if (result) {
                                                         [[STRestKitLoader sharedInstance] updateCurrentUser:result];
                                                     }
                                                     block(result, error, cancellation);
                                                 }];
}

- (UIImage *)currentUserImage {
    if (!_currentUserImage) {
        NSString* url = self.currentUser.imageURL;
        _currentUserImage = [[[STImageCache sharedInstance] cachedImageForImageURL:self.currentUser.imageURL] retain];
        if (!_currentUserImage && !self.userImageCancellation) {
            self.userImageCancellation = [[STImageCache sharedInstance] imageForImageURL:url
                                                                             andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                                                                                 if (!_currentUserImage && image) {
                                                                                     self.userImageCancellation = nil;
                                                                                     _currentUserImage = [image retain];
                                                                                 }
                                                                             }];
        }
    }
    return [[_currentUserImage retain] autorelease];
}

- (void)setCurrentUserImage:(UIImage *)currentUserImage {
    [_currentUserImage autorelease];
    _currentUserImage = [currentUserImage retain];
    [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPIUserUpdatedNotification object:nil];
}

- (UIImage*)currentUserImageForSize:(STProfileImageSize)profileImageSize {
    return self.currentUserImage;
}

- (STCancellation*)alertsWithCallback:(void (^)(NSArray<STAlertItem>* alerts, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/account/alerts/show.json"
                                                     post:NO
                                            authenticated:YES
                                                   params:[NSDictionary dictionary]
                                                  mapping:[STSimpleAlertItem mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  block((id)results, error, cancellation); 
                                              }];
}

- (STCancellation*)alertsWithOnIDs:(NSArray*)onIDs
                            offIDs:(NSArray*)offIDS 
                       andCallback:(void (^)(NSArray<STAlertItem>* alerts, NSError* error, STCancellation* cancellation))block {
    NSString* onString = [onIDs componentsJoinedByString:@","];
    NSString* offString = [offIDS componentsJoinedByString:@","];
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                            onString, @"on",
                            offString, @"off",
                            nil];
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/account/alerts/update.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:params 
                                                  mapping:[STSimpleAlertItem mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  block((id)results, error, cancellation); 
                                              }];
}

- (STCancellation*)shareSettingsWithService:(NSString*)service
                                andCallback:(void (^)(NSArray<STAlertItem>* alerts, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/account/linked/show_share_settings.json"
                                                     post:NO
                                            authenticated:YES
                                                   params:[NSDictionary dictionaryWithObject:service forKey:@"service_name"]
                                                  mapping:[STSimpleAlertItem mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)updateShareSettingsWithService:(NSString*)service
                                            onIDs:(NSArray*)onIDs
                                           offIDs:(NSArray*)offIDS 
                                      andCallback:(void (^)(NSArray<STAlertItem>* alerts, NSError* error, STCancellation* cancellation))block {
    NSString* onString = [onIDs componentsJoinedByString:@","];
    NSString* offString = [offIDS componentsJoinedByString:@","];
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                            onString, @"on",
                            offString, @"off",
                            service, @"service_name",
                            nil];
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/account/linked/update_share_settings.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:params 
                                                  mapping:[STSimpleAlertItem mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  block((id)results, error, cancellation); 
                                              }];
}

- (STCancellation*)linkedAccountsWithCallback:(void (^)(id<STLinkedAccounts> linkedAccounts, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/show.json"
                                                        post:NO
                                               authenticated:YES
                                                      params:[NSDictionary dictionary]
                                                     mapping:[STSimpleLinkedAccounts mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     block(result, error, cancellation); 
                                                 }];
}

- (STCancellation*)removeLinkedAccountWithService:(NSString*)service
                                      andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    
    return [[STRestKitLoader sharedInstance] loadOneWithPath:[NSString stringWithFormat:@"/account/linked/%@/remove.json", service]
                                                        post:YES 
                                               authenticated:YES
                                                      params:[NSDictionary dictionary]
                                                     mapping:[STSimpleBooleanResponse mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     BOOL success = NO;
                                                     if (result) {
                                                         id<STBooleanResponse> response = result;
                                                         success = [response result].boolValue; 
                                                     }
                                                     block(success, error, cancellation);
                                                 }];
}


- (STCancellation*)createEntityWithParams:(NSDictionary*)params
                              andCallback:(void (^)(id<STEntityDetail> entityDetail, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadOneWithPath:@"/entities/create.json"
                                                        post:YES
                                               authenticated:YES
                                                      params:params
                                                     mapping:[STSimpleEntityDetail mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                     if (result) {
                                                         [self.entityDetailCache setObject:result forKey:[result entityID]];
                                                     }
                                                     block(result, error, cancellation);
                                                 }];
}

+ (void)logError:(NSString*)message {
    [[self sharedInstance] createLogWithKey:@"error"
                                      value:message
                                    stampID:nil
                                   entityID:nil
                                     todoID:nil
                                  commentID:nil
                                 activityID:nil
                                andCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
                                    
                                }];
}

- (id<STDatum>)datumForCurrentDatum:(id<STDatum>)datum {
    if ([datum conformsToProtocol:@protocol(STStamp)]) {
        id<STStamp> stamp = (id)datum;
        id<STStamp> local = [self cachedStampForStampID:stamp.stampID];
        if (local && local != stamp) {
            return local;
        }
    }
    return nil;
}

- (STCancellation*)creditingStampsWithUserID:(NSString*)userID 
                                        date:(NSDate*)date 
                                       limit:(NSInteger)limit 
                                      offset:(NSInteger)offset
                                 andCallback:(void (^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                            userID, @"user_id",
                            @"credit", @"scope",
                            [NSNumber numberWithInteger:[date timeIntervalSince1970]], @"before",
                            [NSNumber numberWithInteger:limit], @"limit",
                            [NSNumber numberWithInteger:offset], @"offset",
                            nil];
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/stamps/collection.json"
                                                     post:NO
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleStamp mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  if (results) {
                                                      NSArray<STStamp>* stamps = (id)results;
                                                      for (id<STStamp> stamp in stamps) {
                                                          [self.stampCache setObject:(id)stamp forKey:stamp.stampID];
                                                      }
                                                  }
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)usersWithEmails:(NSArray*)emails 
                       andCallback:(void (^)(NSArray<STUserDetail>* users, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/users/find/email.json"
                                                     post:NO
                                            authenticated:YES
                                                   params:[NSDictionary dictionaryWithObject:[emails componentsJoinedByString:@","] forKey:@"query"] 
                                                  mapping:[STSimpleUserDetail mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  if (results) {
                                                      for (id<STUserDetail> user in results) {
                                                          //TODO cache
                                                      }
                                                  }
                                                  block((id)results, error, cancellation);
                                              }];
}

- (STCancellation*)usersWithPhoneNumbers:(NSArray*)phoneNumbers 
                             andCallback:(void (^)(NSArray<STUserDetail>* users, NSError* error, STCancellation* cancellation))block {
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/users/find/phone.json"
                                                     post:NO
                                            authenticated:YES
                                                   params:[NSDictionary dictionaryWithObject:[phoneNumbers componentsJoinedByString:@","] forKey:@"query"] 
                                                  mapping:[STSimpleUserDetail mapping]
                                              andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
                                                  if (results) {
                                                      for (id<STUserDetail> user in results) {
                                                          //TODO cache
                                                      }
                                                  }
                                                  block((id)results, error, cancellation);
                                              }];
}

- (void)fastPurge {
    [self.entityDetailCache fastMemoryPurge];
    [self.stampCache fastMemoryPurge];
    [self.stampedByCache fastMemoryPurge];
    [self.userCache removeAllObjects];
}

@end

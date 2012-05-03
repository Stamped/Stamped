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

@interface STStampedAPI () <STCacheModelSourceDelegate>

@property (nonatomic, readonly, retain) STCacheModelSource* menuCache;
@property (nonatomic, readonly, retain) STCacheModelSource* stampCache;
@property (nonatomic, readonly, retain) STCacheModelSource* entityDetailCache;

- (void)path:(NSString*)path WithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block;

@end

@implementation STStampedAPI

@synthesize menuCache = _menuCache;
@synthesize stampCache = _stampCache;
@synthesize entityDetailCache = entityDetailCache_;

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
    _menuCache = [[STCacheModelSource alloc] initWithDelegate:self];
    _stampCache = [[STCacheModelSource alloc] initWithDelegate:self];
    entityDetailCache_ = [[STCacheModelSource alloc] initWithDelegate:self];
  }
  return self;
}

- (void)dealloc
{
  [_menuCache release];
  [_stampCache release];
  [entityDetailCache_ release];
  [super dealloc];
}

- (id<STUser>)currentUser {
  return [STSimpleUser userFromLegacyUser:[AccountManager sharedManager].currentUser];
}

- (STCancellation*)stampForStampID:(NSString*)stampID 
                       andCallback:(void(^)(id<STStamp> stamp, NSError* error, STCancellation* cancellation))block {
  NSAssert(stampID != nil,@"stampID must not be nil");
  return [self.stampCache fetchWithKey:stampID callback:block];
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
          [self.stampCache setObject:stamp forKey:stamp.stampID];
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

- (void)createStampWithStampNew:(STStampNew*)stampNew andCallback:(void(^)(id<STStamp> stamp, NSError* error))block {
  NSString* path = @"/stamps/create.json";
  [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                               post:YES
                                             params:stampNew.asDictionaryParams
                                            mapping:[STSimpleStamp mapping]
                                        andCallback:^(id stamp, NSError* error, STCancellation* cancellation) {
                                          block(stamp, error);
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
                                            [self.stampCache removeObjectForKey:stampID];
                                          }
                                          block(stamp != nil, error);
                                        }];
}

- (void)entityResultsForEntitySuggested:(STEntitySuggested*)entitySuggested 
                            andCallback:(void(^)(NSArray<STEntitySearchSection>* sections, NSError* error))block {
  NSString* path = @"/entities/suggested.json";
  [[STRestKitLoader sharedInstance] loadWithPath:path 
                                            post:NO 
                                          params:entitySuggested.asDictionaryParams 
                                         mapping:[STSimpleEntitySearchSection mapping] 
                                     andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                                       block((NSArray<STEntitySearchSection>*)array, error);
                                     }];
}

- (void)entityResultsForEntitySearch:(STEntitySearch*)entitySearch 
                         andCallback:(void(^)(NSArray<STEntitySearchResult>* results, NSError* error))block {
  NSString* path = @"/entities/search.json";
  [[STRestKitLoader sharedInstance] loadWithPath:path
                                            post:NO
                                          params:entitySearch.asDictionaryParams
                                         mapping:[STSimpleEntitySearchResult mapping]
                                     andCallback:^(NSArray *array, NSError *error, STCancellation* cancellation) {
                                       block((NSArray<STEntitySearchResult>*)array, error);
                                     }];
}

- (STCancellation*)entityForEntityID:(NSString*)entityID 
                         andCallback:(void(^)(id<STEntity> entity, NSError* error, STCancellation* cancellation))block {
  return [self entityDetailForEntityID:entityID andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
    block(detail, error, cancellation);
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
                               andCallback:(void(^)(id<STEntityDetail> detail, NSError* error, STCancellation* cancellation))block {
  return [self.entityDetailCache fetchWithKey:entityID callback:block];
}

- (void)entityDetailForSearchID:(NSString*)searchID andCallback:(void(^)(id<STEntityDetail>))block{
  NSOperation* operation = [[STEntityDetailFactory sharedFactory] entityDetailCreatorWithSearchId:searchID andCallbackBlock:block];
  [Util runOperationAsynchronously:operation];
}

- (void)activitiesForYouWithGenericSlice:(STGenericSlice*)slice 
                             andCallback:(void(^)(NSArray<STActivity>* activities, NSError* error))block {
  NSString* path = @"/activity/show.json";
  
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


- (void)createCommentForStampID:(NSString*)stampID 
                      withBlurb:(NSString*)blurb 
                    andCallback:(void(^)(id<STComment> comment, NSError* error))block {
  NSString* path = @"/comments/create.json";
  NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                          stampID, @"stamp_id",
                          blurb, @"blurb",
                          nil];
  [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                               post:YES 
                                             params:params 
                                            mapping:[STSimpleComment mapping] 
                                        andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                          block(result, error);
                                        }];
}

- (void)likeWithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block {
  NSString* path = @"/stamps/likes/create.json";
  [self path:path WithStampID:stampID andCallback:block];
}

- (void)unlikeWithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block {
  NSString* path = @"/stamps/likes/remove.json";
  [self path:path WithStampID:stampID andCallback:block];
}

- (void)todoWithStampID:(NSString*)stampID 
               entityID:(NSString*)entityID 
            andCallback:(void(^)(id<STTodo>,NSError*))block {
  NSString* path = @"/favorites/create.json";
  NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                          stampID, @"stamp_id",
                          entityID, @"entity_id",
                          nil];
  [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                               post:YES 
                                             params:params 
                                            mapping:[STSimpleTodo mapping] 
                                        andCallback:^(id todo, NSError* error, STCancellation* cancellation) {
                                          if (todo) {
                                            id<STTodo> todoObj = todo;
                                            if (todoObj.stamp && todoObj.stamp.stampID) {
                                              [self.stampCache setObject:todoObj.stamp forKey:todoObj.stamp.stampID];
                                            }
                                            else if (stampID) {
                                              [self.stampCache removeObjectForKey:stampID];
                                            }
                                          }
                                          block(todo, error);
                                        }];
}


- (void)todosWithGenericCollectionSlice:(STGenericCollectionSlice*)slice 
                            andCallback:(void(^)(NSArray<STTodo>*,NSError*))block {
  NSString* path = @"/favorites/show.json";
  [[STRestKitLoader sharedInstance] loadWithPath:path
                                            post:NO
                                          params:slice.asDictionaryParams
                                         mapping:[STSimpleTodo mapping]
                                     andCallback:^(NSArray* results, NSError* error, STCancellation* cancellation) {
                                       block((NSArray<STTodo>*)results,error);
                                     }];
}

- (void)isTododWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block {
  //TODO
}

- (void)untodoWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block {
  NSString* path = @"/favorites/remove.json";
  NSDictionary* params = [NSDictionary dictionaryWithObject:entityID forKey:@"entity_id"];
  [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                               post:YES 
                                             params:params 
                                            mapping:[STSimpleTodo mapping] 
                                        andCallback:^(id result, NSError* error, STCancellation* cancellation) {
                                          id<STTodo> todo = result;
                                          if (todo.stamp) {
                                            [self.stampCache setObject:todo.stamp forKey:todo.stamp.stampID];
                                          }
                                          block(error == nil, error);
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
                                          if (stamp) {
                                            [self.stampCache setObject:stamp forKey:stampID];
                                          }
                                          block(stamp, error);
                                        }];
}

- (STCancellation*)objectForCache:(STCacheModelSource*)cache 
                          withKey:(NSString*)key 
                 andCurrentObject:(id)object 
                     withCallback:(void(^)(id model, NSInteger cost, NSError* error, STCancellation* cancellation))block {
  if (cache == self.menuCache) {
    STCancellation* cancellation = [STCancellation cancellation];
    [[STMenuFactory sharedFactory] menuWithEntityId:key andCallbackBlock:^(id<STMenu> menu) {
      if (!cancellation.cancelled) {
        if (menu) {
          block(menu, 1, nil, cancellation);
        }
        else {
          block(nil, -1, [NSError errorWithDomain:[STStampedAPI errorDomain]
                                             code:STStampedAPIErrorUnavailable
                                         userInfo:[NSDictionary dictionaryWithObjectsAndKeys:@"key",key, nil]], cancellation);
        }
      }
    }];
    return cancellation;
  }
  else if (cache == self.stampCache) {
    NSDictionary* params = [NSDictionary dictionaryWithObject:key forKey:@"stamp_id"];
    NSString* path = @"/stamps/show.json";
    STCancellation* cancellation = [[STRestKitLoader sharedInstance] loadWithPath:path 
                                                                             post:NO 
                                                                           params:params 
                                                                          mapping:[STSimpleStamp mapping] 
                                                                      andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation2) {
                                                                        id<STStamp> stamp = nil;
                                                                        if (!cancellation2.cancelled) {
                                                                          if (array && [array count] > 0) {
                                                                            stamp = [array objectAtIndex:0];
                                                                          }
                                                                          if (stamp) {
                                                                            block(stamp, 1, nil, cancellation2);
                                                                          }
                                                                          else {
                                                                            block(nil, -1, error, cancellation2);
                                                                          }
                                                                        }
                                                                      }];
    return cancellation;
  }
  else if (cache == self.entityDetailCache) {
    NSDictionary* params = [NSDictionary dictionaryWithObject:key forKey:@"entity_id"];
    NSString* path = @"/entities/show.json";
    return [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                                        post:NO
                                                      params:params
                                                     mapping:[STSimpleEntityDetail mapping]
                                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                   block(result, 1, error, cancellation);
                                                 }];
  }
  NSAssert2(NO, @"unknown cache (%@) asked for key %@", cache, key);
  return nil;
}

- (void)handleCompletionWithSource:(id<STSource>)source action:(NSString*)action andContext:(STActionContext*)context {
  
  if (source.completionEndpoint) {
    NSMutableDictionary* params = [NSMutableDictionary dictionary];
    if (source.completionData) {
      [params addEntriesFromDictionary:source.completionData];
    }
    [[STRestKitLoader sharedInstance] loadOneWithPath:@"/actions/complete.json"
                                                 post:YES 
                                               params:params mapping:[STSimpleTodo mapping]
                                          andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                            [STDebug log:[NSString stringWithFormat:@"Callback %@ for endpoint %@.\n%@:%@:%@\n%@",
                                                          result ? @"succeeded" : @"failed",
                                                          source.completionEndpoint,
                                                          action,
                                                          source.source,
                                                          source.sourceID,
                                                          params]];
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

@end

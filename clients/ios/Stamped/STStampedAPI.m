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

- (void)path:(NSString*)path WithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block;
- (void)stampsForSlice:(STGenericSlice*)slice 
              withPath:(NSString*)path 
           andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error))block;

@end

@implementation STStampedAPI

@synthesize menuCache = _menuCache;
@synthesize stampCache = _stampCache;

static STStampedAPI* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STStampedAPI alloc] init];
}

+ (STStampedAPI*)sharedInstance {
  return _sharedInstance;
}

- (id)init
{
  self = [super init];
  if (self) {
    _menuCache = [[STCacheModelSource alloc] initWithMainKey:@"entityID" andDelegate:self];
    _stampCache = [[STCacheModelSource alloc] initWithMainKey:@"stampID" andDelegate:self];
  }
  return self;
}

- (id<STUser>)currentUser {
  return [STSimpleUser userFromLegacyUser:[AccountManager sharedManager].currentUser];
}

- (void)stampForStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>))block {
  NSAssert(stampID != nil,@"stampID must not be nil");
  [self.stampCache fetchWithKey:stampID callback:block];
}


- (void)stampsForSlice:(STGenericSlice*)slice 
              withPath:(NSString*)path 
           andCallback:(void(^)(NSArray<STStamp>* stamps, NSError* error))block {
  NSDictionary* params = [slice asDictionaryParams];
  void(^outerBlock)(NSArray*,NSError*) = ^(NSArray* stamps, NSError* error) {
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
      block(array, error);
    }
    else {
      block(nil, error);
    }
    
  };
  [[STRestKitLoader sharedInstance] loadWithPath:path 
                                            post:NO 
                                          params:params 
                                         mapping:[STSimpleStamp mapping] 
                                     andCallback:outerBlock];
  
}

- (void)stampsForInboxSlice:(STGenericCollectionSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block {
  [self stampsForSlice:slice withPath:@"/collections/inbox.json" andCallback:block];
}

- (void)stampsForUserSlice:(STUserCollectionSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block {
  [self stampsForSlice:slice withPath:@"/collections/user.json" andCallback:block];
}

- (void)stampsForFriendsSlice:(STFriendsSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block {
  [self stampsForSlice:slice withPath:@"/collections/friends.json" andCallback:block];
}

- (void)stampsForSuggestedSlice:(STGenericCollectionSlice*)slice andCallback:(void(^)(NSArray<STStamp>*, NSError*))block {
  [self stampsForSlice:slice withPath:@"/collections/suggested.json" andCallback:block];
}

- (void)stampedByForStampedBySlice:(STStampedBySlice*)slice andCallback:(void(^)(id<STStampedBy>, NSError*))block {
  NSString* path = @"/entities/stamped_by.json";
  [[STRestKitLoader sharedInstance] loadOneWithPath:path 
                                               post:NO 
                                             params:[slice asDictionaryParams] 
                                            mapping:[STSimpleStampedBy mapping]
                                        andCallback:^(id stampedBy, NSError* error) {
                                          block(stampedBy, block);
                                        }];
}

- (void)createStampWithStampNew:(STStampNew*)stampNew andCallback:(void(^)(id<STStamp> stamp, NSError* error))block {
  NSString* path = @"/stamps/create.json";
  [[STRestKitLoader sharedInstance] loadOneWithPath:path
                                               post:YES
                                             params:stampNew.asDictionaryParams
                                            mapping:[STSimpleStamp mapping]
                                        andCallback:^(id stamp, NSError* error) {
                                          block(stamp, error);
                                        }];
}

- (void)deleteStampWithStampID:(NSString*)stampID andCallback:(void(^)(BOOL,NSError*))block {
  NSString* path = @"/stamps/remove.json";
  NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
  [[STRestKitLoader sharedInstance] loadOneWithPath:path post:YES params:params mapping:[STSimpleStamp mapping] andCallback:^(id stamp, NSError* error) {
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
                                     andCallback:^(NSArray* array, NSError* error) {
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
                                     andCallback:^(NSArray *array, NSError *error) {
                                       block((NSArray<STEntitySearchResult>*)array, error);
                                     }];
}

- (void)entityForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntity>))block {
  [self entityDetailForEntityID:entityID andCallback:^(id<STEntityDetail> entityDetail, NSError* error) {
    block(entityDetail);
  }];
}

- (void)userDetailForUserID:(NSString*)userID andCallback:(void(^)(id<STUserDetail> userDetail, NSError* error))block {
  NSString* path = @"/users/show.json";
  NSDictionary* params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
  [[STRestKitLoader sharedInstance] loadOneWithPath:path post:NO params:params mapping:[STSimpleUserDetail mapping] andCallback:^(id user, NSError* error) {
    block(user, error);
  }];
}

- (void)userDetailsForUserIDs:(NSArray*)userIDs andCallback:(void(^)(NSArray<STUserDetail>* userDetails, NSError* error))block {
  NSString* path = @"/users/lookup.json";
  NSDictionary* params = [NSDictionary dictionaryWithObject:[userIDs componentsJoinedByString:@","] forKey:@"user_ids"];
  [[STRestKitLoader sharedInstance] loadWithPath:path post:YES params:params mapping:[STSimpleUserDetail mapping] andCallback:^(NSArray* array, NSError* error) {
    block((NSArray<STUserDetail>*)array, error);
  }];
}

- (void)entityDetailForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntityDetail> detail, NSError* error))block {
  NSOperation* operation = [[STEntityDetailFactory sharedFactory] entityDetailCreatorWithEntityId:entityID andCallbackBlock:^(id<STEntityDetail> detail) {
    if (detail) {
      block(detail,nil);
    }
    else {
      block(nil, [NSError errorWithDomain:@"/entities/show.json" code:0 userInfo:[NSDictionary dictionary]]);
    }
  }];
  [Util runOperationAsynchronously:operation];
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
                                     andCallback:^(NSArray* array, NSError* error) {
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
                                     andCallback:^(NSArray* array, NSError* error) {
                                       block((NSArray<STActivity>*)array, error);
                                     }];
}

- (void)menuForEntityID:(NSString*)entityID andCallback:(void(^)(id<STMenu>))block {
  [self.menuCache fetchWithKey:entityID callback:block];
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
                                        andCallback:^(id result, NSError* error) {
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
                                        andCallback:^(id todo, NSError* error) {
                                          if (todo) {
                                            id<STTodo> todoObj = todo;
                                            if (todoObj.stamp && todoObj.stamp.stampID) {
                                              [self.stampCache setObject:todoObj.stamp forKey:todoObj.stamp.stampID];
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
                                     andCallback:^(NSArray* results, NSError* error) {
                                       block((NSArray<STTodo>*)results,error);
                                     }];
}

- (void)isTododWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block {
  
}

- (void)untodoWithEntityID:(NSString*)entityID andCallback:(void(^)(BOOL,NSError*))block {
  NSString* path = @"/favorites/remove.json";
  NSDictionary* params = [NSDictionary dictionaryWithObject:entityID forKey:@"entity_id"];
  [[STRestKitLoader sharedInstance] loadOneWithPath:path post:YES params:params mapping:[STSimpleTodo mapping] andCallback:^(id todo, NSError* error) {
    if (error) {
      [[[[UIAlertView alloc] initWithTitle:@"bad connection" message:@"internet :(" delegate:nil cancelButtonTitle:@"OK" otherButtonTitles:nil] autorelease] show];
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
                                     andCallback:^(id result, NSError* error) {
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
                                        andCallback:^(id result, NSError* error) {
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
                                        andCallback:^(BOOL boolean, NSError *error) {
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
                                        andCallback:^(id result, NSError* error) {
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
                                        andCallback:^(id result, NSError* error) {
                                          block(result, error);
                                        }];
}

- (void)path:(NSString*)path WithStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>,NSError*))block {
  NSDictionary* params = [NSDictionary dictionaryWithObject:stampID forKey:@"stamp_id"];
  [[STRestKitLoader sharedInstance] loadOneWithPath:path post:YES params:params mapping:[STSimpleStamp mapping] andCallback:^(id stamp, NSError* error) {
    if (stamp) {
      [self.stampCache setObject:stamp forKey:stampID];
    }
    block(stamp, error);
  }];
}

- (void)objectForCache:(STCacheModelSource*)cache withKey:(NSString*)key andCurrentObject:(id)object withCallback:(void(^)(id))block {
  if (cache == self.menuCache) {
    [[STMenuFactory sharedFactory] menuWithEntityId:key andCallbackBlock:^(id<STMenu> menu) {
      block(menu);
    }];
  }
  else if (cache == self.stampCache) {
    NSLog(@"key:%@",key);
    NSDictionary* params = [NSDictionary dictionaryWithObject:key forKey:@"stamp_id"];
    NSString* path = @"/stamps/show.json";
    [[STRestKitLoader sharedInstance] loadWithPath:path post:NO params:params mapping:[STSimpleStamp mapping] andCallback:^(NSArray* array, NSError* error) {
      id<STStamp> stamp = nil;
      if (array && [array count] > 0) {
        stamp = [array objectAtIndex:0];
      }
      block(stamp);
    }];
  }
}

@end

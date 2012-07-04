//
//  STUserDetail.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STUser.h"
#import "STDistributionItem.h"

@protocol STUserDetail <STUser>

@property (nonatomic, readonly, copy) NSString* bio;
@property (nonatomic, readonly, copy) NSString* website;
@property (nonatomic, readonly, copy) NSString* location;
@property (nonatomic, readonly, copy) NSString* identifier;
@property (nonatomic, readonly, copy) NSString* searchIdentifier;

@property (nonatomic, readonly, copy) NSNumber* numStamps;
@property (nonatomic, readonly, copy) NSNumber* numStampsLeft;
@property (nonatomic, readonly, copy) NSNumber* numFriends;
@property (nonatomic, readonly, copy) NSNumber* numFollowers;
@property (nonatomic, readonly, copy) NSNumber* numTodos;
@property (nonatomic, readonly, copy) NSNumber* numCredits;
@property (nonatomic, readonly, copy) NSNumber* numCreditsGiven;
@property (nonatomic, readonly, copy) NSNumber* numLikes;
@property (nonatomic, readonly, copy) NSNumber* numLikesGiven;

@property (nonatomic, readonly, copy) NSArray<STDistributionItem>* distribution;

@end

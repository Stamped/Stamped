//
//  STSimpleUserDetail.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleUser.h"
#import "STUserDetail.h"
#import <RestKit/RestKit.h>

@interface STSimpleUserDetail : STSimpleUser <STUserDetail, NSCoding>

@property (nonatomic, readwrite, copy) NSString* bio;
@property (nonatomic, readwrite, copy) NSString* website;
@property (nonatomic, readwrite, copy) NSString* location;
@property (nonatomic, readwrite, copy) NSString* identifier;
@property (nonatomic, readwrite, copy) NSString* searchIdentifier;

@property (nonatomic, readwrite, copy) NSNumber* numStamps;
@property (nonatomic, readwrite, copy) NSNumber* numStampsLeft;
@property (nonatomic, readwrite, copy) NSNumber* numFriends;
@property (nonatomic, readwrite, copy) NSNumber* numFollowers;
@property (nonatomic, readwrite, copy) NSNumber* numTodos;
@property (nonatomic, readwrite, copy) NSNumber* numCredits;
@property (nonatomic, readwrite, copy) NSNumber* numCreditsGiven;
@property (nonatomic, readwrite, copy) NSNumber* numLikes;
@property (nonatomic, readwrite, copy) NSNumber* numLikesGiven;

@property (nonatomic, readwrite, copy) NSArray<STDistributionItem>* distribution;

+ (RKObjectMapping*)mapping;

@end

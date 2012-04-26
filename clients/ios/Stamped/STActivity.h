//
//  STActivity.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STActivityReference.h"
#import "STActivityObjects.h"

@protocol STActivity <NSObject>

@property (nonatomic, readonly, copy) NSString* header;
@property (nonatomic, readonly, copy) NSString* body;
@property (nonatomic, readonly, copy) NSString* footer;

@property (nonatomic, readonly, copy) NSNumber* benefit;
@property (nonatomic, readonly, copy) NSDate* created;
@property (nonatomic, readonly, copy) NSString* icon;
@property (nonatomic, readonly, copy) NSString* image;

@property (nonatomic, readonly, copy) NSArray<STUser>* subjects;
@property (nonatomic, readonly, copy) NSString* verb;
@property (nonatomic, readonly, retain) id<STActivityObjects> objects;
@property (nonatomic, readonly, retain) id<STAction> action;

@property (nonatomic, readonly, retain) NSArray<STActivityReference>* headerReferences;
@property (nonatomic, readonly, retain) NSArray<STActivityReference>* bodyReferences;
@property (nonatomic, readonly, retain) NSArray<STActivityReference>* footerReferences;

@end

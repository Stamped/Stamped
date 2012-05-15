//
//  STSimpleActivity.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STActivity.h"

@interface STSimpleActivity : NSObject <STActivity, NSCoding>

@property (nonatomic, readwrite, copy) NSString* header;
@property (nonatomic, readwrite, copy) NSString* body;
@property (nonatomic, readwrite, copy) NSString* footer;

@property (nonatomic, readwrite, copy) NSNumber* benefit;
@property (nonatomic, readwrite, copy) NSDate* created;
@property (nonatomic, readwrite, copy) NSString* icon;
@property (nonatomic, readwrite, copy) NSString* image;

@property (nonatomic, readwrite, copy) NSArray<STUser>* subjects;
@property (nonatomic, readwrite, copy) NSString* verb;
@property (nonatomic, readwrite, retain) id<STActivityObjects> objects;
@property (nonatomic, readwrite, retain) id<STAction> action;

@property (nonatomic, readwrite, retain) NSArray<STActivityReference>* headerReferences;
@property (nonatomic, readwrite, retain) NSArray<STActivityReference>* bodyReferences;
@property (nonatomic, readwrite, retain) NSArray<STActivityReference>* footerReferences;

+ (RKObjectMapping*)mapping;

@end

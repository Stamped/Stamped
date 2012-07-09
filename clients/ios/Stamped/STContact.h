//
//  STContact.h
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STUserDetail.h"
#import "STCancellation.h"
#import <RestKit/RestKit.h>

@interface STContact : NSObject

+ (NSArray*)contactsForOffset:(NSInteger)offset andLimit:(NSInteger)limit nextOffset:(NSInteger*)nextOffset finished:(BOOL*)finished;

+ (STCancellation*)contactsFromFacebookWithOffset:(NSInteger)offset 
                                            limit:(NSInteger)limit 
                                      andCallback:(void (^)(NSArray*, NSError*, STCancellation*))block;

@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSArray* phoneNumbers;
@property (nonatomic, readwrite, copy) NSArray* emailAddresses;
@property (nonatomic, readwrite, assign) BOOL invite;
@property (nonatomic, readwrite, retain) id<STUserDetail> userDetail;
@property (nonatomic, readwrite, retain) UIImage* image;
@property (nonatomic, readonly, retain) NSString* primaryEmailAddress;
@property (nonatomic, readwrite, copy) NSString* imageURL;
@property (nonatomic, readwrite, copy) NSString* facebookID;

@end

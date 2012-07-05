//
//  STContact.h
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STUserDetail.h"

@interface STContact : NSObject

+ (NSArray*)contactsForOffset:(NSInteger)offset andLimit:(NSInteger)limit nextOffset:(NSInteger*)nextOffset finished:(BOOL*)finished;

@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSArray* phoneNumbers;
@property (nonatomic, readwrite, copy) NSArray* emailAddresses;
@property (nonatomic, readwrite, retain) id<STUserDetail> userDetail;

@end

//
//  STMenuPrice.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STMenuPrice <NSObject>

@property (nonatomic, readonly, retain) NSString* title;
@property (nonatomic, readonly, retain) NSString* price;
@property (nonatomic, readonly, assign) NSInteger calories;
@property (nonatomic, readonly, retain) NSString* unit;
@property (nonatomic, readonly, retain) NSString* currency;

@end

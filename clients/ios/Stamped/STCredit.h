//
//  STCredit.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STCredit <NSObject>

@property (nonatomic, readonly, copy) NSString* userID;
@property (nonatomic, readonly, copy) NSString* screenName;
@property (nonatomic, readonly, copy) NSString* stampID;
@property (nonatomic, readonly, copy) NSString* colorPrimary;
@property (nonatomic, readonly, copy) NSString* colorSecondary;
@property (nonatomic, readonly, copy) NSString* privacy;

@end

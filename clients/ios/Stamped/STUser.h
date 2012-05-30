//
//  STUser.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STUser <NSObject>

@property (nonatomic, readonly, copy) NSString* name;
@property (nonatomic, readonly, copy) NSString* userID;
@property (nonatomic, readonly, copy) NSString* screenName;
@property (nonatomic, readonly, copy) NSString* primaryColor;
@property (nonatomic, readonly, copy) NSString* secondaryColor;
@property (nonatomic, readonly, copy) NSNumber* privacy;
@property (nonatomic, readonly, copy) NSString* imageURL;

@end

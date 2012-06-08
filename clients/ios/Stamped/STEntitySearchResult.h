//
//  STEntitySearchResult.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STEntitySearchResult <NSObject>

@property (nonatomic, readonly, copy) NSString* searchID;
@property (nonatomic, readonly, copy) NSString* title;
@property (nonatomic, readonly, copy) NSString* subtitle;
@property (nonatomic, readonly, copy) NSString* category;
@property (nonatomic, readonly, copy) NSNumber* distance;
@property (nonatomic, readonly, copy) NSString* icon;

@end

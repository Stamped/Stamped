//
//  STBadge.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STBadge <NSObject>

@property (nonatomic, readonly, copy) NSString* genre;
@property (nonatomic, readonly, copy) NSString* userID;

@end

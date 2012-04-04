//
//  STMention.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STMention <NSObject>

@property (nonatomic, readonly, copy) NSString* screenName;
@property (nonatomic, readonly, copy) NSString* userID;
@property (nonatomic, readonly, copy) NSArray* indices;

@end

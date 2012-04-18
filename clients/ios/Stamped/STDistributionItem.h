//
//  STDistributionItem.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STDistributionItem <NSObject>

@property (nonatomic, readonly, copy) NSString* category;
@property (nonatomic, readonly, copy) NSNumber* count;
@property (nonatomic, readonly, copy) NSString* name;
@property (nonatomic, readonly, copy) NSString* icon;

@end

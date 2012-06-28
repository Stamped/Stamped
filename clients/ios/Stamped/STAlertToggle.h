//
//  STAlertToggle.h
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STAlertToggle <NSObject>

@property (nonatomic, readonly, copy) NSString* toggleID;
@property (nonatomic, readonly, copy) NSString* type;
@property (nonatomic, readonly, copy) NSNumber* value;

@end

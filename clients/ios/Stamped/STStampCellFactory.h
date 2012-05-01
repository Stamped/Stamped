//
//  STStampCellFactory.h
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTableViewCellFactory.h"

@interface STStampCellFactory : NSObject <STTableViewCellFactory>

+ (STStampCellFactory*)sharedInstance;

@end

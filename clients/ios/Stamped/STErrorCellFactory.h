//
//  STErrorCellFactory.h
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTableViewCellFactory.h"

@interface STErrorCellFactory : NSObject <STTableViewCellFactory>

+ (STErrorCellFactory*)sharedInstance;

@end

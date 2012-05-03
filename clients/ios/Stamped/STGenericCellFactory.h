//
//  STGenericCellFactory.h
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTableViewCellFactory.h"

@interface STGenericCellFactory : NSObject <STTableViewCellFactory>

+ (STGenericCellFactory*)sharedInstance;

@end

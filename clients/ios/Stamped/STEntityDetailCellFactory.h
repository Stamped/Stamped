//
//  STEntityDetailCellFactory.h
//  Stamped
//
//  Created by Landon Judkins on 5/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTableViewCellFactory.h"

@interface STEntityDetailCellFactory : NSObject <STTableViewCellFactory>

+ (STEntityDetailCellFactory*)sharedInstance;

@end

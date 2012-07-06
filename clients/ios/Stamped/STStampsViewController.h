//
//  STStampsViewController.h
//  Stamped
//
//  Created by Landon Judkins on 7/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRestViewController.h"
#import "STCache.h"

@interface STStampsViewController : STRestViewController

- (id)initWithCache:(STCache*)cache;

+ (STCancellation*)creditsViewWithUserID:(NSString*)userID
                             andCallback:(void (^)(UIViewController* controller, NSError* error, STCancellation* cancellation))block;

@end

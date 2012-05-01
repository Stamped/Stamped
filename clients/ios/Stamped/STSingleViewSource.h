//
//  STSingleViewSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTableDelegate.h"

@interface STSingleViewSource : NSObject <STTableDelegate>

- (id)initWithView:(UIView*)view;

@end

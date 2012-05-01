//
//  STTableDelegator.h
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTableDelegate.h"

@interface STTableDelegator : NSObject <STTableDelegate>

- (void)appendTableDelegate:(id<STTableDelegate>)tableDelegate;
- (void)appendTableDelegate:(id<STTableDelegate>)tableDelegate withSectionMapping:(NSInteger)sectionMapping;

@end

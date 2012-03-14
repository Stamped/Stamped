//
//  STResizeDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STResizeDelegate <NSObject>

- (void)view:(UIView*)view willChangeHeightBy:(CGFloat)delta over:(CGFloat)seconds;

@end

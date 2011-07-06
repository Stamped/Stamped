//
//  STNavigationBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STNavigationBar.h"


@implementation STNavigationBar

- (void)drawRect:(CGRect)rect {
  UIImage* img = [UIImage imageNamed:@"toolbar_bg"];
  [img drawInRect:CGRectMake(0, 0, rect.size.width, rect.size.height)];
}

@end

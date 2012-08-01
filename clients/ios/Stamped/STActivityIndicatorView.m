//
//  STActivityIndicatorView.m
//  Stamped
//
//  Created by Landon Judkins on 7/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActivityIndicatorView.h"
#import "Util.h"

@interface STActivityIndicatorView ()

@end

@implementation STActivityIndicatorView

- (void)setFrame:(CGRect)frame {
    CGRect layerFrameBefore = self.layer.frame;
    [super setFrame:frame];
    if ([[UIDevice currentDevice].systemVersion doubleValue] < 5.0) {
        NSLog(@"changin frame");
        self.layer.frame = [Util centeredAndBounded:layerFrameBefore.size inFrame:[Util originRectWithRect:self.frame]];
    }
}

@end

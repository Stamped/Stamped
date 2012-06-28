//
//  STTextChunk.h
//  Stamped
//
//  Created by Landon Judkins on 6/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STChunk.h"

@interface STTextChunk : STChunk

- (id)initWithPrev:(STChunk*)chunk text:(NSString*)text font:(UIFont*)font color:(UIColor*)color;
- (id)initWithPrev:(STChunk*)chunk text:(NSString*)text font:(UIFont*)font color:(UIColor*)color kerning:(CGFloat)kerning;

@end

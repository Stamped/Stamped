//
//  STLikeButton.h
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STAStampButton.h"
#import "STStamp.h"

@interface STLikeButton : STAStampButton

- (id)initWithStamp:(id<STStamp>)stamp;

@end

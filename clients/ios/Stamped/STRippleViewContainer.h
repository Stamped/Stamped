//
//  STRippleViewContainer.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"

@interface STRippleViewContainer : STViewContainer

- (id)initWithDelegate:(id<STViewDelegate>)delegate
          primaryColor:(NSString*)primaryColor 
     andSecondaryColor:(NSString*)secondaryColor;

@property (nonatomic, readonly, retain) STViewContainer* body;

@end

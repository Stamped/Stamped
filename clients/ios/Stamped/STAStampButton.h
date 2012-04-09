//
//  STAStampButton.h
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STToolbarButton.h"
#import "STStamp.h"

@interface STAStampButton : STToolbarButton

- (id)initWithStamp:(id<STStamp>)stamp normalOffImage:(UIImage*)normalOffImage offText:(NSString*)offText andOnText:(NSString*)onText;

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

@end

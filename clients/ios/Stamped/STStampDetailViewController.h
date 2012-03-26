//
//  STStampDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STViewController.h"

@class Stamp;
@class STStampDetailToolbar;

@interface STStampDetailViewController : STViewController

- (id)initWithStamp:(Stamp*)stamp;

@property (nonatomic, retain) IBOutlet STStampDetailToolbar* toolbar;

@end

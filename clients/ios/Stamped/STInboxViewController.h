//
//  STInboxViewController.h
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTableViewController.h"
#import "STLazyList.h"
#import "STRestViewController.h"
#import "Stamps.h"

@class STSliderScopeView, Stamps;
@interface STInboxViewController : STRestViewController {
    STSliderScopeView *_slider;
    Stamps *_stamps;
    STStampedAPIScope _scope;
}

@end

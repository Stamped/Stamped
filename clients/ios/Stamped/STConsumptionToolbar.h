//
//  STConsumptionToolbar.h
//  Stamped
//
//  Created by Landon Judkins on 5/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STConsumptionToolbarItem.h"
#import "STStampedAPI.h"
#import "STToolbarView.h"
#import "STSliderScopeView.h"

@class STConsumptionToolbar;

@protocol STConsumptionToolbarDelegate <NSObject>

- (void)toolbar:(STConsumptionToolbar*)toolbar 
  didMoveToItem:(STConsumptionToolbarItem*)item 
           from:(STConsumptionToolbarItem*)previous;

@end

@interface STConsumptionToolbar : STToolbarView

- (id)initWithRootItem:(STConsumptionToolbarItem*)item andScope:(STStampedAPIScope)scope;

@property (nonatomic, readwrite, assign) id<STConsumptionToolbarDelegate> delegate;
@property (nonatomic, readonly, retain) STSliderScopeView* slider;

+ (void)setupConfigurations;

@end

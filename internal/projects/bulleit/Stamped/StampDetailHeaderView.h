//
//  StampDetailHeaderView.h
//  Stamped
//
//  Created by Jake Zien on 11/21/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <QuartzCore/QuartzCore.h>
#import "Stamp.h"
#import "Entity.h"

@protocol StampDetailHeaderViewDelegate <NSObject>
- (IBAction)handleEntityTap:(id)sender;
@end

@interface StampDetailHeaderView : UIView

@property (nonatomic, assign) BOOL inverted;
@property (nonatomic, retain) Stamp* stamp;
@property (nonatomic, retain) NSString* title;
@property (nonatomic, retain) id <StampDetailHeaderViewDelegate> delegate;
@property (nonatomic, assign) BOOL hideArrow;

- (void)setEntity:(Entity*)entity;

@end
//
//  STHoverToolbar.h
//  Stamped
//
//  Created by Landon Judkins on 6/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"
#import "STEntityDetail.h"
#import "STViewContainer.h"

@interface STHoverToolbar : UIView

- (id)initWithStamp:(id<STStamp>)stamp;

- (id)initWithEntity:(id<STEntityDetail>)entityDetail;

- (void)positionInParent;

@property (nonatomic, readwrite, assign) id target;
@property (nonatomic, readwrite, assign) SEL commentAction;
@property (nonatomic, readwrite, assign) SEL shareAction;

@end
